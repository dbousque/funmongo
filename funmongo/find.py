

from funmongo.config import db
from funmongo.conversion import pymongo_to_funmongo
from funmongo.utils import hasattr_n_val
import sys

class IterDocs:

	def __init__(self, model, cursor, apply_func, pred=None, add_data=None, skip=0, limit=0, unsafe=False):
		self.cursor = cursor
		self.model = model
		self.apply_func = apply_func
		self.pred = pred
		self.add_data = add_data
		self.taken = 0
		self.skip = skip
		self.limit = limit
		self.unsafe = unsafe

	def __iter__(self):
		return self

	def __next__(self):
		# doing a while loop to avoid tail recursion if pred(ret) is false
		# or add_data(ret) is None
		while True:
			while self.skip > 0:
				nex = self.cursor.next()
				self.skip -= 1
			if self.limit > 0 and self.taken >= self.limit:
				raise StopIteration
			nex = self.cursor.next()
			ret = pymongo_to_funmongo(self.model, nex, unsafe=self.unsafe)
			if self.pred:
				if not self.pred(ret):
					continue
			if self.add_data:
				add = self.add_data(ret)
				if add is None:
					continue
				if self.apply_func:
					ret = (self.apply_func(ret), add)
				else:
					ret = (ret, add)
			elif self.apply_func:
				ret = self.apply_func(ret)
			self.taken += 1
			return ret

def restrict_to_subtype(model, sel):
	if hasattr_n_val(model, "funmongo_is_child", True):
		sel["funmongo_subtype"] = model.__name__
	return sel

def find_maybe_one_doc(model, sel, unsafe=False, **kwargs):
	sel = restrict_to_subtype(model, sel)
	res = db[model.collec].find_one(sel, **kwargs)
	if not res:
		return None
	return pymongo_to_funmongo(model, res, unsafe=unsafe)

def find_one_doc(model, sel, unsafe=False, **kwargs):
	doc = find_maybe_one_doc(model, sel, unsafe=unsafe, **kwargs)
	if not doc:
		raise Exception("Document in collection " + model.collec + " and query " + str(sel) + " not found")
	return doc

def maybe_from_id(model, ident, unsafe=False):
	return find_maybe_one_doc(model, {"_id": ident}, unsafe=unsafe)

def from_id(model, ident, unsafe=False):
	return find_one_doc(model, {"_id": ident}, unsafe=unsafe)

def find_docs(model, sel=None, raw_cursor=False, pred=None, add_data=None, apply_func=None, skip=0, limit=0, unsafe=False, **kwargs):
	if sel is None:
		sel = {}
	sel = restrict_to_subtype(model, sel)
	if pred or add_data:
		if raw_cursor:
			raise Exception("find_docs cannot be called with raw_cursor=True and pred, apply_func or add_data defined")
		cur = db[model.collec].find(sel, **kwargs)
		return IterDocs(model, cur, apply_func, pred=pred, add_data=add_data, skip=skip, limit=limit, unsafe=unsafe)
	kwargs["limit"] = limit
	kwargs["skip"] = skip
	cur = db[model.collec].find(sel, **kwargs)
	if raw_cursor:
		if apply_func is not id:
			raise Exception("find_docs cannot be called with raw_cursor=True and pred, apply_func or add_data defined")
		return cur
	return IterDocs(model, cur, apply_func, unsafe=unsafe)

def get_all(model, unsafe=False):
	return find_docs(model, {}, unsafe=unsafe)

def remove_all(model, sel=None, **kwargs):
	if sel is None:
		sel = {}
	sel = restrict_to_subtype(model, sel)
	db[model.collec].remove(sel, **kwargs)