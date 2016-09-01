

from datetime import datetime
from db import db
from config import verbose
from utils import my_print, hasattr_n_val
from errors import *

def find_valid_parent_docs(current_doc):
	parents = current_doc.__bases__
	ret = []
	for par in parents:
		if par is not Document:
			if hasattr_n_val(par, "is_funmongo_doc", True):
				ret.extend(find_valid_parent_docs(par))
				ret.append(par)
	return list(set(ret))

class Document:

	# magic number
	is_funmongo_doc = True

	def update_structure_with_parents(self, parents):
		for par in parents:
			for key in par.structure.keys():
				if key in self.structure:
					raise Exception(error_field_already_defined(self, key, par))
			self.structure.update(par.structure)

	def check_child_same_module_as_parents(self, parents):
		for par in parents:
			mod = __import__(par.__module__, fromlist=[""])
			if not hasattr(mod, type(self).__name__):
				raise Exception(subtype_not_found(model, type(self).__name__))

	def update_structure_if_needed(self):
		if not hasattr_n_val(type(self), "funmongo_already_done", True):
			type(self).funmongo_already_done = False
			parents = find_valid_parent_docs(type(self))
			self.check_child_same_module_as_parents(parents)
			if len(parents) > 0:
				type(self).funmongo_is_child = True
				self.update_structure_with_parents(parents)
			type(self).funmongo_already_done = True

	def funmongo_init(self, args={}, unsafe=False):
		if not hasattr(type(self), "structure"):
			type(self).structure = {}
		self.update_structure_if_needed()
		err = self.invalid_document()
		if err:
			raise Exception(err)
		self.doc_items = {}
		if hasattr_n_val(type(self), "funmongo_is_child", True):
			self["funmongo_subtype"] = type(self).__name__
		for key,val in args.items():
			if unsafe:
				self.unsafe_set(key, val)
			else:
				self[key] = val
		if hasattr(self, "init_func") and self.init_func:
			self.init_func()

	def __init__(self, **kwargs, unsafe=False):
		self.funmongo_init(args=kwargs, unsafe=unsafe)

	def invalid_document(self):
		if not hasattr(self, "collec"):
			return "Invalid document " + type(self).__name__ + " : no 'collec' field defined" 
		return None

	def actual_setitem(self, attr, val):
		self.doc_items[attr] = val

	def unsafe_set(self, attr, val):
		actual_setitem(attr, val)

	def __setitem__(self, attr, val):
		if attr == "funmongo_subtype":
			self.actual_setitem(attr, val)
			return
		if not isinstance(attr, str):
			raise Exception(error_field_str(attr))
		# checking if the field is expected or additional_fields is set
		if not attr in self.structure:
			if not hasattr_n_val(self, "additional_fields", True):
				raise Exception(error_unknown_field(self, attr, "Cannot set field "))
		else:
			# checking that the value has the right type defined in structure
			if not isinstance(val, self.structure[attr]):
				raise Exception(error_wrong_val_type(self, attr, val))
			# checking that the field is not already set or that this field is mutable
			if attr in self.doc_items:
				if not hasattr_n_val(self, "all_mutable", True):
					if not hasattr(self, "mutable") or attr not in self.mutable:
						raise Exception(error_not_mutable(self, attr))
		self.actual_setitem(attr, val)

	def __getitem__(self, key):
		return self.doc_items[key]

	def __str__(self):
		st = ""
		if hasattr(self, '_id'):
			st += str(self._id) + ":\n"
		if not hasattr(self, 'doc_items'):
			return st
		return st + str(self.doc_items)

	def validate(self):
		self.update_structure_if_needed()
		is_child = hasattr_n_val(type(self), "funmongo_is_child", True)
		err = self.invalid_document()
		if err:
			raise Exception(err)
		for key,typ in self.structure.items():
			if not key in self.doc_items:
				raise Exception("Missing field : " + key + self.error_info())
			if not isinstance(self.doc_items[key], typ):
				raise Exception("Bad type for field " + key + self.error_info())
		expected_nb_fields = len(self.structure.keys())
		if is_child:
			expected_nb_fields += 1
		if not hasattr_n_val(self, "additional_fields", True) and len(self.doc_items.keys()) != expected_nb_fields:
			for key in self.doc_items.keys():
				if not key in self.structure and (not is_child or key != "funmongo_subtype"):
					raise Exception(error_unknown_field(self, key, "Invalid field "))

	def is_on_db(self):
		return hasattr(self, '_id')

	def remove(self):
		if hasattr(self, _id):
			db[self.collec].remove_one({"_id": self._id})
			del self.__dict__['_id'];

	def save(self, unsafe=False):
		if not unsafe:
			self.validate()
		if hasattr(self, '_id'):
			if verbose:
				my_print("saving existing document, removing first...")
			db[self.collec].remove_one({"_id": self._id})
			if verbose:
				my_print("removed")
			self.doc_items.update({"_id": self._id})
		if verbose:
			my_print("saving document...")
		db[self.collec].insert_one(self.doc_items)
		self._id = self.doc_items["_id"]
		del self.doc_items["_id"]
		if verbose:
			my_print("saved : " + str(self._id))

	def error_info(self):
		st = "\nModel : " + type(self).__name__ + "\nCollection : "
		collec = None
		if hasattr(self, "collec"):
			collec = self.collec
		st += str(collec)
		if hasattr(self, "subtype"):
			st += "\nSubtype : " + self.subtype
		st += "\nDocument : "
		st += str(self)
		st += " (might be incompletely loaded when the error occured)"
		return st

class MyDoc0(Document):
	collec = "my_collec0"
	structure = {
		"my_field1": str,
		"my_field2": int
	}
	mutable = ["my_field2"]
	additional_fields = False

def init(obj):
	obj.ok = 1

class MyDoc(Document):
	collec = "my_collec"
	structure = {
		"my_field1": str,
		"my_field2": int,
		"my_field3": float
	}
	init_func = init

class MyDocChild(MyDoc):
	structure = {
		"my_field4": str,
		"salut": int
	}

class Product(Document):
	collec = "products"
	structure = {
		"name": str,
		"price": float,
		"currency": str
	}

class EuropeanProduct(Product):
	structure = {
		"EUvalidated": bool
	}

class FrenchProduct(EuropeanProduct):
	structure = {
		"RCSvalidated": bool
	}

class FreeDoc(Document):
	collec = "freedocs"
	additional_fields = True

"""lol = MyDoc()
lol2 = MyDocChild(salut=1)
lol3 = MyDocChild()
lol4 = MyDoc0()
print(lol4)
lol4["my_field1"] = "1"
lol4["my_field2"] = 2
lol4["my_field2"] = 3
print(lol4)"""
fr = FrenchProduct(name="salut", price=12.8, currency="$", EUvalidated=True, RCSvalidated=False)
fr2 = FrenchProduct()
fr["name"] = "dodo"
fr.save()
free = FreeDoc()
free["lolz1"] = 1
free["lolz1"] = "str"
free["lolz2"] = fr._id
free.save()