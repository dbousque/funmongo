

from tests.test_models1 import EuropeanProduct
from funmongo.funmongo.utils import get_collection, new_collection
from funmongo.find import find_docs, remove_all

new_collec = new_collection("products")
prods = find_docs(EuropeanProduct, raw_cursor=True)
new_collec.insert_many(prods)
remove_all(EuropeanProduct)

"""for i in range(100000):
	prod = EuropeanProduct(name="lol", price=12.8, currency="$", EUvalidated=True)
	prod.save()"""