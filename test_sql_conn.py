from IPython import get_ipython
import os

ip = get_ipython()
if ip:
    ip.run_line_magic("load_ext", "sql")
    try:
        ip.run_line_magic("sql", "mysql+mysqlconnector://root:***@localhost:3306/")
        print("Success with /")
    except Exception as e:
        print("Failed with /", repr(e))

    try:
        ip.run_line_magic("sql", "mysql+mysqlconnector://root:***@localhost:3306")
        print("Success without /")
    except Exception as e:
        print("Failed without /", repr(e))
