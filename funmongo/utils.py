

import sys
from funmongo.config import options

def my_print(st):
	sys.stdout.write(st)
	sys.stdout.write("\n")

def hasattr_n_val(obj, attr, val):
	if hasattr(obj, attr) and getattr(obj, attr) == val:
		return True
	return False

def read_batch(cur, n=1000):
	ret = []
	i = 0
	for elt in cur:
		if i >= n:
			break
		ret.append(elt)
		i += 1
	return ret

def get_collection(model):
	return options["db"][model.collec]

def new_collection(collec_name):
	return options["db"][collec_name]

def get_db(model):
	return options["db"]