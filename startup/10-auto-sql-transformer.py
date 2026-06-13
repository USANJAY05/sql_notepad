import os
from pathlib import Path
from urllib.parse import quote_plus

from IPython import get_ipython
from dotenv import load_dotenv


dotenv_path = Path.home() / ".ipython" / "profile_default" / "startup" / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)
else:
    print(f"Warning: {dotenv_path} not found.")

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD", "")
host = os.getenv("DB_HOST")
dbname = os.getenv("DB_NAME", "")
port = os.getenv("DB_PORT", "3306")

if not all([user, host]):
    print("Missing required DB credentials: DB_USER and DB_HOST.")
else:
    encoded_password = quote_plus(password)
    auth = f"{user}:{encoded_password}" if password else user
    database = f"/{dbname}" if dbname else "/"
    conn_str = f"mysql+mysqlconnector://{auth}@{host}:{port}{database}"

    ip = get_ipython()
    if ip:
        try:
            ip.run_line_magic("load_ext", "sql")
            ip.run_line_magic("sql", conn_str)

            def sql(query):
                return ip.run_line_magic("sql", query)

            def auto_sql_transformer(lines):
                joined = "".join(lines)
                stripped = joined.strip()
                if not stripped:
                    return lines

                sql_keywords = {
                    "SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP",
                    "ALTER", "SHOW", "DESCRIBE", "DESC", "EXPLAIN", "USE",
                    "WITH",
                }
                first_word = stripped.split(None, 1)[0].upper()

                if first_word in sql_keywords:
                    return [f'sql("""{joined}""")\n']

                return lines

            if auto_sql_transformer not in ip.input_transformers_cleanup:
                ip.input_transformers_cleanup.append(auto_sql_transformer)

            ip.user_ns["sql"] = sql
            print("SQL Auto Setup Loaded.")
        except Exception as e:
            print(f"Failed to connect to SQL: {e}")
