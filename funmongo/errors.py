

def error_field_str(attr):
	return "Documents' attributes must be of type str, given : " + repr(attr)
def error_unknown_field(doc, attr, start):
	return start + repr(attr) + ", not in structure and additional_fields not set to True" + doc.error_info()
def error_wrong_val_type(doc, attr, val):
	if type(doc.structure[attr]) is list:
		typ = [typ.__name__ for typ in doc.structure[attr]]
	else:
		typ = doc.structure[attr].__name__
	return "Bad type for field " + repr(attr) + " : gave " + repr(type(val).__name__) + " but expected type " + repr(typ) + " (value : " + repr(val) + ")" + doc.error_info()
def error_not_mutable(doc, attr):
	return "The field " + repr(attr) + " is already set and was not specified as mutable" + doc.error_info()
def error_field_already_defined(doc, key, par):
	return "Field " + repr(key) + " in object " + par.__name__ + " was already defined in the structure of another object inherited by " + type(doc).__name__
def subtype_not_found(model, child_name):
	return "Child model " + repr(child_name) + " was not found in the same module as his parent model " + repr(model.__name__) + ", where it should be"