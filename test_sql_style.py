from IPython import get_ipython
import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
ip = get_ipython()
if ip:
    ip.run_line_magic("load_ext", "sql")
    print("Setting config...")
    ip.run_line_magic("config", "SqlMagic.style = 'PLAIN_COLUMNS'")
    ip.run_line_magic("sql", "DROP TABLE IF EXISTS test;")
    ip.run_line_magic("sql", "CREATE TABLE test (id INT);")
    ip.run_line_magic("sql", "INSERT INTO test VALUES (1);")
    res = ip.run_line_magic("sql", "SELECT * FROM test;")
    print("Result string format:", str(res))
    print("SUCCESS!")
