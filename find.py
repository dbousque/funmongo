

from srcs.funmongo.db import db
from pymongo import DESCENDING
from conversion import pymongo_to_funmongo
import sys

class IterDocs:

	def __init__(self, model, cursor, apply_func, pred=None, add_data=None, skip=0, limit=None, unsafe=False):
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
			if self.limit and self.taken >= self.limit:
				raise StopIteration
			nex = self.cursor.next()
			ret = pymongo_to_funmongo(self.model, nex, self.unsafe)
			if self.pred:
				if not self.pred(ret):
					continue
			if self.add_data:
				add = self.add_data(ret)
				if add is None:
					continue
				ret = (self.apply_func(ret), add)
			else:
				ret = self.apply_func(ret)
			self.taken += 1
			return ret

def restrict_to_subtype(model, sel):
	if hasattr(model, "subtype"):
		sel["subtype"] = model.subtype
	return sel

def find_maybe_one_doc(model, sel, unsafe=False):
	sel = restrict_to_subtype(model, sel)
	res = db[model.collec].find_one(sel)
	if not res:
		return None
	return pymongo_to_funmongo(model, res, unsafe)

def find_one_doc(model, sel, unsafe=False):
	doc = find_maybe_one(model, sel, unsafe=unsafe)
	if not doc:
		raise Exception("Document in collection " + model.collec + " and query " + str(sel) + " not found")
	return doc

def maybe_from_id(model, ident, unsafe=False):
	return find_maybe_one_doc(model, {"_id": ident}, unsafe=unsafe)

def from_id(model, ident, unsafe=False):
	return find_one_doc(mode, {"_id": ident}, unsafe=unsafe)

def find_docs(model, sel, pred=None, add_data=None, apply_func=id, skip=0, limit=None, unsafe=False):
	sel = restrict_to_subtype(model, sel)
	if pred or add_data:
		cur = db[model.collec].find(sel).sort("date_added", DESCENDING)
		return IterDocs(model, cur, apply_func, pred=pred, add_data=add_data, skip=skip, limit=limit, unsafe=unsafe)
	cur = db[model.collec].find(sel).sort("date_added", DESCENDING).skip(skip)
	if limit:
		cur = cur.limit(limit)
	return IterDocs(model, cur, apply_func, unsafe=unsafe)