

from pymongo import MongoClient
from config import uri, db_name

if uri is None or uri is "":
	client = MongoClient()
else:
	client = MongoClient(uri)
db = client[db_name]