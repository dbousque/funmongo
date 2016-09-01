

import sys

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