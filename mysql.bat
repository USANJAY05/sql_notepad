@echo off
:: Wrapper script for the MySQL notebook environment
if "%~1"=="" (
    python install.py help
) else (
    python install.py %*
)
