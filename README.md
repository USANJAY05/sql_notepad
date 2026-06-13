# SQL Notepad

Turn your Jupyter Notebook into a powerful SQL editor. Run SQL directly in notebook cells—no extra magic commands required.

## 🚀 One-Line Installation

Open your terminal and run the command for your operating system:

**macOS & Linux:**
```bash
curl -sSL https://raw.githubusercontent.com/USANJAY05/sql_notepad/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
iwr -useb https://raw.githubusercontent.com/USANJAY05/sql_notepad/main/install.ps1 | iex
```

The script will ask you if you want to install it globally (recommended) or locally. It will also securely ask for your MySQL database credentials so you never have to type them again.

## 💻 How to Use

If you chose the **Global Install**, you can now start your notebook from *any* folder on your computer! Just type:

```bash
mysql start
```

*(If you are on macOS/Linux and didn't restart your terminal yet, use `~/.local/bin/mysql start`)*

Jupyter Notebook will open in your browser, automatically connected to your database. You can just type `SELECT * FROM ...` in any cell!

### Available Commands

| Command | Description |
|---|---|
| `mysql start` | Start the notebook in the background |
| `mysql stop` | Stop the background notebook process |
| `mysql restart` | Restart the notebook server |
| `mysql modify` | Update your database username/password |
| `mysql status` | Check if the notebook is running |
| `mysql uninstall` | Completely remove SQL Notepad from your computer |

*(Note: By default, it opens the current directory. To open the notebook in a specific folder, just pass the path: `mysql start ~/Desktop`)*

## 🛠️ Local Testing / Manual Setup

If you chose the **Local Testing** option during installation, the app was downloaded to a `./sql_notepad` folder right where you were standing, instead of being installed globally. 

To run it, you must enter that folder first:
```bash
cd sql_notepad
./mysql start
```
