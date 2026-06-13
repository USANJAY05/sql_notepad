#!/usr/bin/env bash
set -e

echo "========================================"
echo "   SQL Notepad Automated Installer"
echo "========================================"

REPO_URL="https://github.com/USANJAY05/sql_notepad.git"
INSTALL_DIR="$HOME/.ipython/sql_notepad"
BIN_DIR="$HOME/.local/bin"

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

echo "Setting up global 'mysql' command..."
mkdir -p "$BIN_DIR"
ln -sf "$INSTALL_DIR/mysql" "$BIN_DIR/mysql"

# Add to PATH if necessary
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "Adding $BIN_DIR to PATH in shell configuration..."
    
    # Check bash
    if [ -f "$HOME/.bashrc" ]; then
        if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.bashrc"; then
            echo '\n# SQL Notepad' >> "$HOME/.bashrc"
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
        fi
    fi
    
    # Check zsh
    if [ -f "$HOME/.zshrc" ]; then
        if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.zshrc"; then
            echo '\n# SQL Notepad' >> "$HOME/.zshrc"
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
        fi
    fi
    
    export PATH="$BIN_DIR:$PATH"
fi

echo "Starting setup..."
./mysql install

echo "========================================"
echo "Installation complete!"
echo "You can now run 'mysql start' from ANY directory."
echo "Note: You may need to restart your terminal or run 'source ~/.zshrc' (or .bashrc) for the 'mysql' command to be available."
echo "========================================"
