# SQL Notepad

This project sets up a Jupyter Notebook environment that auto-connects to MySQL and lets you run SQL directly in notebook cells without explicit magic commands.

## Requirements

- Python 3.8 or newer
- Git

## Quick Install (macOS/Linux)

You can automatically install the entire environment globally using this one-liner:

```bash
curl -sSL https://raw.githubusercontent.com/USANJAY05/sql_notepad/main/install.sh | bash
```

*This downloads the application to a hidden folder (`~/.ipython/sql_notepad`) and automatically installs the `mysql` command globally to your system so you can use it from any terminal.*

## Manual Setup

If you prefer to install manually:

1. Clone the repository into your Jupyter config folder:
   ```bash
   git clone https://github.com/USANJAY05/sql_notepad.git ~/.ipython/sql_notepad
   cd ~/.ipython/sql_notepad
   ```

2. Run the installer:
   - **macOS/Linux**: `./mysql install`
   - **Windows**: `mysql install` (or `mysql.bat install`)

3. (Optional) Create a global alias or symlink to `~/.ipython/sql_notepad/mysql` so you can use the command from anywhere.

The installer will ask for your MySQL username, password, host, port, and (optionally) your database name.

## Commands

Use the provided wrapper script to manage your environment from anywhere:

- `./mysql install` — Install packages and ask for DB credentials
- `./mysql modify`  — Change saved DB credentials
- `./mysql start [dir]` — Start Jupyter Notebook (defaults to current directory)
- `./mysql stop`    — Stop the Jupyter process
- `./mysql restart [dir]` — Restart Jupyter Notebook
- `./mysql status`  — Check whether Jupyter is running
- `./mysql uninstall` — Remove the environment

*(On Windows, use `mysql` instead of `./mysql`)*

## Dynamic Workspace

By default, Jupyter Notebook dynamically launches serving whatever directory you invoke `./mysql start` from. 

If you want to open Jupyter in a specific directory (like your Desktop or your entire home folder), you can pass that path directly to the start command:

```bash
./mysql start ~/Desktop
# or
./mysql start /
```

## Configuration

Credentials are saved to `db.env` and copied to `~/.ipython/profile_default/startup/.env`.

Supported variables:
```text
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_NAME=your_database_name
DB_PORT=3306
```
*(If `DB_NAME` is left blank, you can connect to your MySQL server globally without selecting a specific database).*
