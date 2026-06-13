import sys
from sqlalchemy.engine.url import make_url

url1 = make_url("mysql+mysqlconnector://root:admin@127.0.0.1:3306/")
url2 = make_url("mysql+mysqlconnector://root:admin@127.0.0.1:3306")
print(f"URL1 database: {url1.database!r}")
print(f"URL2 database: {url2.database!r}")
