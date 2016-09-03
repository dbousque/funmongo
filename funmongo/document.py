

from datetime import datetime
from funmongo.config import options, db
from funmongo.utils import my_print, hasattr_n_val
from funmongo.errors import *
from copy import copy

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
			par_structure = {}
			if hasattr(par, "funmongo_raw_structure"):
				par_structure = par.funmongo_raw_structure
			elif hasattr(par, "structure"):
				par_structure = par.structure
			for key in par_structure.keys():
				if key in type(self).structure:
					raise Exception(error_field_already_defined(self, key, par))
			type(self).structure.update(par_structure)
			if hasattr(par, "indexes"):
				for ind in par.indexes:
					if ind not in type(self).indexes:
						type(self).indexes.append(ind)
			if hasattr(par, "mutable"):
				for mut in par.mutable:
					if mut not in type(self).mutable:
						type(self).mutable.append(mut)

	def check_child_same_module_as_parents(self, parents):
		for par in parents:
			mod = __import__(par.__module__, fromlist=[""])
			if not hasattr(mod, type(self).__name__):
				raise Exception(subtype_not_found(model, type(self).__name__))

	def update_structure_if_needed(self):
		if not hasattr_n_val(type(self), "funmongo_already_done", True):
			if not hasattr(type(self), "structure"):
				type(self).structure = {}
			if not hasattr(type(self), "indexes"):
				type(self).indexes = []
			if not hasattr(type(self), "mutable"):
				type(self).mutable = []
			type(self).funmongo_raw_structure = copy(type(self).structure)
			type(self).funmongo_already_done = False
			parents = find_valid_parent_docs(type(self))
			self.check_child_same_module_as_parents(parents)
			if len(parents) > 0:
				type(self).funmongo_is_child = True
				if len(parents) > 1:
					type(self).funmongo_parents = parents
				type(self).indexes.append("funmongo_subtype")
				self.update_structure_with_parents(parents)
			for ind in type(self).indexes:
				if type(ind) is str:
					db[self.collec].create_index(ind)
				else:
					db[self.collec].create_index([ind])
			type(self).funmongo_already_done = True

	def funmongo_init(self, args=None, unsafe=False):
		if args is None:
			args = {}
		self.update_structure_if_needed()
		self.doc_items = {}
		if hasattr_n_val(type(self), "funmongo_is_child", True):
			if hasattr(type(self), "funmongo_parents"):
				types = [type(self).__name__]
				for par in type(self).funmongo_parents:
					types.append(par.__name__)
				self["funmongo_subtype"] = types
			else:
				self["funmongo_subtype"] = type(self).__name__
		for key,val in args.items():
			if unsafe:
				self.unsafe_set(key, val)
			else:
				self[key] = val
		if hasattr(self, "init_func") and self.init_func:
			self.init_func()

	def __init__(self, **kwargs):
		self.funmongo_init(args=kwargs, unsafe=False)

	def invalid_document(self):
		if not hasattr(self, "collec"):
			return "Invalid document " + type(self).__name__ + " : no 'collec' field defined" 
		return None

	def actual_setitem(self, attr, val):
		self.doc_items[attr] = val

	def unsafe_set(self, attr, val):
		self.actual_setitem(attr, val)

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

	def __delitem__(self, key):
		if not key in self.doc_items:
			raise Exception("Field " + key + " does not exist in the document")
		del self.doc_items[key]

	def keys():
		return self.doc_items.keys()

	def values():
		return self.doc_items.values()

	def items():
		return self.doc_items.items()

	def __iter__(self):
		return self.doc_items.__iter__()

	def __str__(self):
		st = ""
		if hasattr(self, '_id'):
			st += str(self._id) + ":\n"
		if not hasattr(self, 'doc_items'):
			return st
		return st + str(self.doc_items)

	def validate(self):
		err = self.invalid_document()
		if err:
			raise Exception(err)
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
			db[self.collec].delete_one({"_id": self._id})
			del self.__dict__['_id']

	def save(self, unsafe=False):
		if not unsafe:
			self.validate()
		if hasattr(self, '_id'):
			if options["verbose"]:
				my_print("saving existing document, replacing...")
			ret = db[self.collec].replace_one({"_id": self._id}, self.doc_items)
			if "_id" in self.doc_items:
				if self.doc_items["_id"] != self._id:
					raise Exception("Unexpected : returned id is not the same as the one before")
				del self.doc_items["_id"]
			if options["verbose"]:
				my_print("replaced : " + str(self._id))
		else:
			if options["verbose"]:
				my_print("saving document...")
			ret = db[self.collec].insert_one(self.doc_items)
			if options["verbose"]:
				my_print("saved : " + str(self.doc_items["_id"]))
			self._id = ret.inserted_id
			del self.doc_items["_id"]
		return ret

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

"""lol = MyDoc()
lol2 = MyDocChild(salut=1)
lol3 = MyDocChild()
lol4 = MyDoc0()
print(lol4)
lol4["my_field1"] = "1"
lol4["my_field2"] = 2
lol4["my_field2"] = 3
print(lol4)"""
"""fr = FrenchProduct(name="salut", price=12.8, currency="$", EUvalidated=True, RCSvalidated=False)
fr2 = FrenchProduct()
fr["name"] = "dodo"
fr.save()
free = FreeDoc()
free["lolz1"] = 1
free["lolz1"] = "str"
free["lolz2"] = fr._id
free.save()
del free["lolz1"]
free.save()
lolz = FrenchProduct(name="salut")"""

"""from utils import get_collection
from bson import ObjectId
from find import find_docs

fr = FrenchProduct()
print(fr.indexes)
print(fr.mutable)
collec = get_collection(FrenchProduct)
print(collec.find_one({"_id": ObjectId("57c75db578b1044a655cb055")}))
find_docs(EuropeanProduct)"""