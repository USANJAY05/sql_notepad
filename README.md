# MySQL Notebook

This project sets up a Jupyter Notebook environment that auto-connects to MySQL and lets you run SQL directly in notebook cells.

## Requirements

- Python 3.8 or newer
- MySQL access details in `db.env`

## Install

Install sets up the Python environment and asks for your MySQL username, password, host, database name, and port.

Windows:

```bat
install.bat
```

macOS/Linux:

```sh
./install.sh
```

Cross-platform Python command:

```sh
python install.py install
```

`setup.bat` and `python install.py setup` still work as aliases for install.

## Modify Credentials

Use this whenever the MySQL username, password, host, database, or port changes.

Windows:

```bat
modify.bat
```

Cross-platform Python command:

```sh
python install.py modify
```

## Run

Windows:

```bat
run.bat
```

macOS/Linux:

```sh
./run.sh
```

Cross-platform Python command:

```sh
python install.py start
```

## Stop

Windows:

```bat
stop.bat
```

macOS/Linux:

```sh
./stop.sh
```

Cross-platform Python command:

```sh
python install.py stop
```

## Restart

Windows:

```bat
restart.bat
```

Cross-platform Python command:

```sh
python install.py restart
```

## Configuration

Credentials are saved to `db.env` and copied to:

```text
~/.ipython/profile_default/startup/.env
```

Supported variables:

```text
DB_USER=root
DB_PASSWORD=admin@123
DB_HOST=127.0.0.1
DB_NAME=your_database_name
DB_PORT=3306
```
