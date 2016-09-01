

def invalid_message(model, obj, mess):
	return "Invalid document encountered when loading it from collection " + repr(model.collec) + " ; raw object : " + str(obj) + "\nException : " + mess

def pymongo_to_funmongo(model, obj, unsafe=False):
	if "funmongo_subtype" in obj:
		mod = __import__(model.__module__, fromlist=[""])
		if not hasattr(mod, obj["subtype"]):
			raise Exception(subtype_not_found(model, obj["subtype"]))
		model = getattr(mod, obj["subtype"])
	ident = obj["_id"]
	del obj["_id"]
	try:
		ret = model(**obj, unsafe=unsafe)
		ret._id = ident
		if not unsafe:
			ret.validate()
		return ret
	except Exception as e:
		raise Exception(invalid_message(model, obj, str(e)))