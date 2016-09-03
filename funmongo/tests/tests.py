

from document import Document, find_valid_parent_docs
from utils import get_collection
from copy import copy
from tests.test_models1 import *
from tests.test_models2 import *

def test_std_doc():
	doc = StdDoc(field1="lolz", field2="", field3=12)
	assert not hasattr(doc, "_id")
	doc.save()
	assert hasattr(doc, "_id")
	assert find_valid_parent_docs(type(doc)) == []
	# not mutable field
	mutated = False
	try:
		doc["field3"] = 1
		mutated = True
	except:
		pass
	assert mutated is False
	# mutable field but wrong type
	mutated = False
	try:
		doc["field1"] = 1
		mutated = True
	except:
		pass
	assert mutated is False
	# mutable and should have no errors
	doc["field1"] = "looo"
	doc.save()
	assert doc["field1"] == "looo"
	collec = get_collection(doc)
	elts = list(collec.find({"_id": doc._id}))
	assert len(elts) == 1
	assert elts[0]["field1"] == "looo"

def test_std_all_mutable():
	doc = StdDocMutable(field1="lolz", field2="", field3=12)
	assert not hasattr(doc, "_id")
	doc.save()
	assert hasattr(doc, "_id")
	assert find_valid_parent_docs(type(doc)) == []
	# mutable field
	mutated = False
	try:
		doc["field3"] = 1
		mutated = True
	except:
		pass
	assert mutated is True
	# mutable field but wrong type
	mutated = False
	try:
		doc["field1"] = 1
		mutated = True
	except:
		pass
	assert mutated is False
	# mutable and should have no errors
	doc["field1"] = "looo"
	doc.save()
	assert doc["field1"] == "looo"
	collec = get_collection(doc)
	elts = list(collec.find({"_id": doc._id}))
	assert len(elts) == 1
	assert elts[0]["field1"] == "looo"

def test_not_same_module():
	try:
		doc = NotSameModuleChild()
		raise Exception("Initialization should have failed, not same module")
	except:
		pass

def test_inheritance():
	fr = FrenchProduct()
	fields = copy(EuropeanProduct.structure)
	fields.update(Product.structure)
	fields.update(FrenchProduct.funmongo_raw_structure)
	assert type(fr).structure == fields

test_funcs = [test_std_doc, test_std_all_mutable, test_not_same_module, test_inheritance]