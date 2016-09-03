

from tests.tests import test_funcs
from utils import my_print
from config import set_db_name, set_verbose

set_db_name("funmongo_tests")
set_verbose(False)
success = 0
failure = 0
fails = []
for func in test_funcs:
	try:
		func()
		my_print("✔ " + func.__name__)
		success += 1
	except Exception as e:
		my_print(repr(e))
		my_print("✖ " + func.__name__)
		failure += 1
		fails.append(func.__name__)

if len(fails) == 0:
	my_print("\n" + "✔ All tests passed")
else:
	my_print("\n" + "✖ " + str(success) + " passed, " + str(failure) + " failed : ")
	for fail in fails:
		my_print("    " + fail)