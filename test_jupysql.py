from IPython.terminal.interactiveshell import TerminalInteractiveShell
import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
ip = TerminalInteractiveShell.instance()
ip.run_line_magic("load_ext", "sql")
res = ip.run_line_magic("sql", "SELECT 1 as num;")
print("Result string format:", str(res))
print("SUCCESS!")
