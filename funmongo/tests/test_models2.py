

from tests.test_models1 import NotSameModuleParent

class NotSameModuleChild(NotSameModuleParent):
	structure = {
		"field2": str
	}