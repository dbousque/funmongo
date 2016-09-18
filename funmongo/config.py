

from pymongo import MongoClient

options = {
	"uri": None,
	"db_name": "funmongo_default",
	"verbose": True,
	"db": None
}

def set_db():
	global options
	if options["uri"] is None or options["uri"] is "":
		client = MongoClient()
	else:
		client = MongoClient(options["uri"])
	options["db"] = client[options["db_name"]]

def set_db_name(db_name):
	global options
	options["db_name"] = db_name
	set_db()

def set_uri(uri):
	global options
	options["uri"] = uri
	set_db()

def set_verbose(verbose):
	global options
	options["verbose"] = verbose
	set_db()

set_db()