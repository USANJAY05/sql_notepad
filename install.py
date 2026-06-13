#!/usr/bin/env python3
"""
Cross-platform environment manager for the MySQL notebook setup.

Works on Windows, macOS, and Linux.

Commands:
    python install.py install
    python install.py modify
    python install.py start
    python install.py stop
    python install.py restart
    python install.py status
    python install.py uninstall
"""

from __future__ import annotations

import getpass
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path


HOME = Path.home()
PROJECT_DIR = Path(__file__).resolve().parent
GLOBAL_DIR = HOME / ".ipython" / "sql_notepad"
IS_GLOBAL = (PROJECT_DIR == GLOBAL_DIR)

if IS_GLOBAL:
    VENV_DIR = HOME / ".ipython" / "sqlenv"
    IPYTHON_DIR = HOME / ".ipython"
else:
    VENV_DIR = PROJECT_DIR / "sqlenv"
    IPYTHON_DIR = PROJECT_DIR / ".ipython"

STARTUP_DIR = IPYTHON_DIR / "profile_default" / "startup"
REQUIREMENTS_FILE = PROJECT_DIR / "requirements.txt"
ENV_FILE = PROJECT_DIR / "db.env"
STARTUP_SOURCE = PROJECT_DIR / "startup" / "10-auto-sql-transformer.py"
PID_FILE = PROJECT_DIR / "jupyter.pid"
LOG_FILE = PROJECT_DIR / "jupyter.log"
PORT = 8888

if sys.platform == "win32":
    PYTHON_BIN = VENV_DIR / "Scripts" / "python.exe"
else:
    PYTHON_BIN = VENV_DIR / "bin" / "python"


DEFAULT_REQUIREMENTS = """notebook
ipython
ipython-sql
prettytable==0.7.2
mysql-connector-python
python-dotenv
"""


SAMPLE_ENV_CONTENT = """# Database Configuration
DB_USER=root
DB_PASSWORD=admin@123
DB_HOST=127.0.0.1
DB_NAME=your_database_name
DB_PORT=3306
"""


STARTUP_SCRIPT_CONTENT = '''"""
Auto SQL Transformer for Jupyter/IPython.
Enables direct SQL queries without explicit magic commands.
"""

import os
from pathlib import Path
from urllib.parse import quote_plus

from IPython import get_ipython
from dotenv import load_dotenv


startup_dir = Path(__file__).resolve().parent
dotenv_path = startup_dir / ".env"

if not dotenv_path.exists():
    print(f"Warning: {dotenv_path} not found.")
else:
    load_dotenv(dotenv_path)

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD", "")
host = os.getenv("DB_HOST")
dbname = os.getenv("DB_NAME", "")
port = os.getenv("DB_PORT", "3306")

if not all([user, host]):
    print("Missing required DB credentials: DB_USER and DB_HOST.")
    print("Please check your .env file.")
else:
    encoded_password = quote_plus(password)
    auth = f"{user}:{encoded_password}" if password else user
    database = f"/{dbname}" if dbname else ""
    conn_str = f"mysql+mysqlconnector://{auth}@{host}:{port}{database}"

    ip = get_ipython()
    if ip:
        try:
            ip.run_line_magic("load_ext", "sql")
            ip.run_line_magic("sql", conn_str)

            def sql(query):
                """Execute a SQL query using IPython SQL magic."""
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
                    return [f'sql("""{joined}""")\\n']

                return lines

            if auto_sql_transformer not in ip.input_transformers_cleanup:
                ip.input_transformers_cleanup.append(auto_sql_transformer)

            ip.user_ns["sql"] = sql

            db_info = f"{user}@{host}:{port}"
            if dbname:
                db_info += f"/{dbname}"

            print("SQL Auto Setup Loaded.")
            print(f"Connected to: {db_info}")
            print("Usage: type SQL directly, for example: SELECT * FROM users;")
        except Exception as exc:
            print(f"Failed to connect to SQL: {exc}")
'''


def print_step(message: str) -> None:
    print(f"\n{message}")


def print_error(message: str) -> None:
    print(f"\nError: {message}")
    sys.exit(1)


def ensure_requirements_file() -> None:
    if REQUIREMENTS_FILE.exists():
        return

    print_step("Creating requirements.txt with default packages...")
    REQUIREMENTS_FILE.write_text(DEFAULT_REQUIREMENTS, encoding="utf-8")


def check_python() -> None:
    print_step("Checking Python availability...")
    if sys.version_info < (3, 8):
        print_error("Python 3.8 or higher is required.")
    print(f"Found Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")


def create_venv() -> None:
    if VENV_DIR.exists():
        print_step(f"Virtual environment already exists at {VENV_DIR}")
        return

    print_step(f"Creating virtual environment at {VENV_DIR}...")
    subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)


def install_packages() -> None:
    ensure_requirements_file()
    print_step(f"Installing packages from {REQUIREMENTS_FILE}...")
    subprocess.run([str(PYTHON_BIN), "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([str(PYTHON_BIN), "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)], check=True)


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")

    return values


def prompt_value(label: str, default: str = "", secret: bool = False) -> str:
    prompt = f"{label}"
    if default:
        shown_default = "********" if secret else default
        prompt += f" [{shown_default}]"
    prompt += ": "

    if not sys.stdin.isatty():
        return default

    value = getpass.getpass(prompt) if secret else input(prompt)
    if value == "" and default:
        return default
    return value


def write_env_file(path: Path, values: dict[str, str]) -> None:
    content = "\n".join(
        [
            "# Database Configuration",
            f"DB_USER={values['DB_USER']}",
            f"DB_PASSWORD={values['DB_PASSWORD']}",
            f"DB_HOST={values['DB_HOST']}",
            f"DB_NAME={values['DB_NAME']}",
            f"DB_PORT={values['DB_PORT']}",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_db_credentials() -> dict[str, str]:
    existing = parse_env_file(ENV_FILE)
    startup_existing = parse_env_file(STARTUP_DIR / ".env")
    defaults = {
        "DB_USER": existing.get("DB_USER") or startup_existing.get("DB_USER") or "root",
        "DB_PASSWORD": existing.get("DB_PASSWORD") or startup_existing.get("DB_PASSWORD") or "",
        "DB_HOST": existing.get("DB_HOST") or startup_existing.get("DB_HOST") or "127.0.0.1",
        "DB_NAME": existing.get("DB_NAME") or startup_existing.get("DB_NAME") or "",
        "DB_PORT": existing.get("DB_PORT") or startup_existing.get("DB_PORT") or "3306",
    }

    print_step("Database credentials")
    print("Press Enter to keep the value shown in brackets.")

    values = {
        "DB_USER": prompt_value("MySQL user", defaults["DB_USER"]),
        "DB_PASSWORD": prompt_value("MySQL password", defaults["DB_PASSWORD"], secret=True),
        "DB_HOST": prompt_value("MySQL host", defaults["DB_HOST"]),
        "DB_NAME": prompt_value("Database name (optional, type 'none' to clear)", defaults["DB_NAME"]),
        "DB_PORT": prompt_value("MySQL port", defaults["DB_PORT"]),
    }

    if values["DB_NAME"].lower() == "none":
        values["DB_NAME"] = ""

    if not values["DB_USER"]:
        print_error("MySQL user is required.")
    if not values["DB_HOST"]:
        print_error("MySQL host is required.")
    if not values["DB_PORT"]:
        values["DB_PORT"] = "3306"

    return values


def configure_credentials() -> None:
    values = collect_db_credentials()
    write_env_file(ENV_FILE, values)
    write_env_file(STARTUP_DIR / ".env", values)
    print(f"Saved credentials to {ENV_FILE}")
    print(f"Saved Jupyter startup credentials to {STARTUP_DIR / '.env'}")


def setup_jupyter_startup() -> None:
    print_step(f"Preparing Jupyter startup directory at {STARTUP_DIR}...")
    STARTUP_DIR.mkdir(parents=True, exist_ok=True)

    startup_dest = STARTUP_DIR / "10-auto-sql-transformer.py"
    if STARTUP_SOURCE.exists():
        shutil.copy2(STARTUP_SOURCE, startup_dest)
    else:
        startup_dest.write_text(STARTUP_SCRIPT_CONTENT, encoding="utf-8")
    print(f"Startup script ready: {startup_dest}")

    if not ENV_FILE.exists() and not (STARTUP_DIR / ".env").exists():
        ENV_FILE.write_text(SAMPLE_ENV_CONTENT, encoding="utf-8")


def local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def read_pid() -> int | None:
    try:
        return int(PID_FILE.read_text(encoding="utf-8").strip())
    except (FileNotFoundError, ValueError):
        return None


def process_running(pid: int) -> bool:
    if pid <= 0:
        return False

    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def remove_stale_pid() -> None:
    if PID_FILE.exists():
        PID_FILE.unlink()


def jupyter_command(target_dir: str | None = None) -> list[str]:
    nb_dir = str(Path(target_dir).expanduser().resolve()) if target_dir else str(Path.cwd())
    return [
        str(PYTHON_BIN),
        "-m",
        "jupyter",
        "notebook",
        "--ip=0.0.0.0",
        f"--port={PORT}",
        "--no-browser",
        f"--notebook-dir={nb_dir}",
    ]


def start_jupyter(target_dir: str | None = None) -> None:
    print_step("Starting Jupyter Notebook...")

    if not PYTHON_BIN.exists():
        print("Virtual environment not found. Running installation automatically...")
        check_python()
        create_venv()
        install_packages()
        setup_jupyter_startup()
        configure_credentials()
        print_step("Resuming Jupyter Notebook startup...")

    existing_pid = read_pid()
    if existing_pid and process_running(existing_pid):
        print(f"Jupyter already appears to be running with PID {existing_pid}.")
        print(f"Local URL: http://localhost:{PORT}")
        return
    remove_stale_pid()

    env = os.environ.copy()
    if not IS_GLOBAL:
        env["IPYTHONDIR"] = str(IPYTHON_DIR)

    with LOG_FILE.open("ab") as log:
        proc = subprocess.Popen(
            jupyter_command(target_dir),
            cwd=str(PROJECT_DIR),
            stdout=log,
            stderr=subprocess.STDOUT,
            env=env,
            start_new_session=(sys.platform != "win32"),
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
        )

    PID_FILE.write_text(str(proc.pid), encoding="utf-8")
    time.sleep(1)

    if proc.poll() is not None:
        remove_stale_pid()
        print_error(f"Jupyter exited early. Check the log: {LOG_FILE}")

    print("Jupyter Notebook is running in the background.")
    print(f"Log file: {LOG_FILE}")
    print(f"PID: {proc.pid}")
    print("Access it at:")
    print(f"  Local:   http://localhost:{PORT}")
    print(f"  Network: http://{local_ip()}:{PORT}")
    print("If Jupyter asks for a token, copy it from the log file.")


def stop_jupyter() -> None:
    print_step("Stopping Jupyter Notebook...")

    pid = read_pid()
    if not pid:
        print("No PID file found. Jupyter may already be stopped.")
        return

    if not process_running(pid):
        print(f"No running process found for PID {pid}. Removing stale PID file.")
        remove_stale_pid()
        return

    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], check=False)
        else:
            os.kill(pid, signal.SIGTERM)
        remove_stale_pid()
        print("Jupyter Notebook stopped.")
    except OSError as exc:
        print_error(f"Could not stop PID {pid}: {exc}")


def restart_jupyter(target_dir: str | None = None) -> None:
    stop_jupyter()
    start_jupyter(target_dir)


def check_status() -> None:
    print_step("Checking Jupyter status...")

    pid = read_pid()
    if pid and process_running(pid):
        print(f"Jupyter is running with PID {pid}.")
        print(f"Local URL: http://localhost:{PORT}")
        print(f"Log file: {LOG_FILE}")
        return

    if pid:
        remove_stale_pid()
    print("Jupyter is not running.")


def uninstall_environment() -> None:
    print_step("Uninstalling SQL notebook environment...")
    response = input(
        "This will remove the virtual environment and installed startup files. Continue? (yes/no): "
    ).strip().lower()

    if response not in {"yes", "y"}:
        print("Uninstall cancelled.")
        return

    stop_jupyter()

    if VENV_DIR.exists():
        shutil.rmtree(VENV_DIR)
        print(f"Removed {VENV_DIR}")

    for path in [ENV_FILE, STARTUP_DIR / ".env", STARTUP_DIR / "10-auto-sql-transformer.py"]:
        if path.exists():
            path.unlink()
            print(f"Removed {path}")

    remove_stale_pid()
    print("Uninstall complete.")


def print_completion_message() -> None:
    print("\nSetup complete.")
    print("\nQuick start:")
    print("  ./mysql install")
    print("  ./mysql modify")
    print("  ./mysql start")
    print("  ./mysql stop")
    print("  ./mysql restart")
    print("  ./mysql status")
    print("  ./mysql uninstall")
    print("\nNote: On Windows, use 'mysql' or 'mysql.bat' instead of './mysql'.")


def print_help() -> None:
    print("SQL notebook environment manager")
    print("\nCommands:")
    print("  install     Install packages and ask for DB credentials")
    print("  modify      Change saved DB credentials")
    print("  start [dir] Start Jupyter Notebook in the background (dir defaults to current)")
    print("  stop        Stop the Jupyter process started by this script")
    print("  restart [dir] Restart Jupyter Notebook")
    print("  status      Check whether Jupyter is running")
    print("  uninstall   Remove the environment and startup files")
    print("  help        Show this message")


def main() -> None:
    command = sys.argv[1].lower() if len(sys.argv) > 1 else "install"

    try:
        if command in {"help", "-h", "--help"}:
            print_help()
        elif command in {"setup", "install"}:
            check_python()
            create_venv()
            install_packages()
            setup_jupyter_startup()
            configure_credentials()
            print_completion_message()
        elif command == "modify":
            setup_jupyter_startup()
            configure_credentials()
            print("Credentials updated. Restart Jupyter to use the new values.")
        elif command in {"start", "run"}:
            target_dir = sys.argv[2] if len(sys.argv) > 2 else None
            start_jupyter(target_dir)
        elif command == "stop":
            stop_jupyter()
        elif command == "restart":
            target_dir = sys.argv[2] if len(sys.argv) > 2 else None
            restart_jupyter(target_dir)
        elif command == "status":
            check_status()
        elif command == "uninstall":
            uninstall_environment()
        else:
            print_error(f"Unknown command: {command}")
    except subprocess.CalledProcessError as exc:
        print_error(f"Command failed: {exc}")
    except KeyboardInterrupt:
        print("\nOperation interrupted.")
        sys.exit(1)


if __name__ == "__main__":
    main()
