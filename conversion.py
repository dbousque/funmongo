

def invalid_message(model, obj, mess):
	return "Invalid document encountered when loading it from collection " + repr(model.collec) + " ; raw object : " + str(obj) + "\nException : " + mess

def pymongo_to_funmongo(model, obj, unsafe=False):
	if "funmongo_subtype" in obj:
		mod = __import__(model.__module__, fromlist=[""])
		typ = obj["funmongo_subtype"] if type(obj["funmongo_subtype"]) is str else obj["funmongo_subtype"][0]
		if not hasattr(mod, typ):
			raise Exception(subtype_not_found(model, typ))
		model = getattr(mod, typ)
	ident = obj["_id"]
	del obj["_id"]
	try:
		ret = model.__new__(model)
		ret = ret.funmongo_init(args=obj, unsafe=unsafe)
		ret._id = ident
		if not unsafe:
			ret.validate()
		return ret
	except Exception as e:
		raise Exception(invalid_message(model, obj, str(e)))