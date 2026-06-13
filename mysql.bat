@echo off
:: Wrapper script for the MySQL notebook environment
set SCRIPT_DIR=%~dp0
if "%~1"=="" (
    python "%SCRIPT_DIR%install.py" help
) else (
    python "%SCRIPT_DIR%install.py" %*
)
