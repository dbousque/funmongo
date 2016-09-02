

import pymongo
from document import Document

class StdDoc(Document):
	collec = "stddoc"
	structure = {
		"field1": str,
		"field2": str,
		"field3": int
	}
	mutable = ["field1"]

class StdDocMutable(Document):
	collec = "stddocmut"
	structure = {
		"field1": str,
		"field2": str,
		"field3": int
	}
	all_mutable = True

class NotSameModuleParent(Document):
	collec = "not_same_module"
	structure = {
		"field1": str
	}

class Product(Document):
	collec = "new_products"
	structure = {
		"name": str,
		"price": float,
		"currency": str
	}
	mutable = ["price"]
	indexes = ["name", ("price", pymongo.DESCENDING)]

class EuropeanProduct(Product):
	structure = {
		"EUvalidated": bool
	}
	mutable = ["EUvalidated"]

class FrenchProduct(EuropeanProduct):
	structure = {
		"RCSvalidated": bool
	}
	mutable = ["RCSvalidated"]
	indexes = ["RCSvalidated"]

class FreeDoc(Document):
	collec = "freedocs"
	additional_fields = True