#!/usr/bin/env bash
set -e

echo "========================================"
echo "   SQL Notepad Automated Installer"
echo "========================================"

REPO_URL="https://github.com/USANJAY05/sql_notepad.git"
INSTALL_DIR="$HOME/sql_notepad"

if ! command -v git >/dev/null 2>&1; then
    echo "Error: git is required but not installed."
    exit 1
fi

if [ -d "$INSTALL_DIR" ]; then
    echo "Directory $INSTALL_DIR already exists."
    echo "Updating repository..."
    cd "$INSTALL_DIR"
    git pull origin main
else
    echo "Cloning repository to $INSTALL_DIR..."
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

chmod +x mysql install.sh

echo "Starting setup..."
./mysql install
