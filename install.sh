#!/usr/bin/env bash
set -e

echo "========================================"
echo "   SQL Notepad Automated Installer"
echo "========================================"

echo "Select installation mode:"
echo "1) Global Install (Installs to ~/.ipython/sql_notepad, adds 'mysql' command globally)"
echo "2) Local Testing (Installs to ./sql_notepad in current directory, no global commands)"

# Read from /dev/tty so it works even if piped via curl
while true; do
    read -p "Choice [1/2]: " -n 1 mode < /dev/tty
    echo
    if [[ "$mode" == "1" || "$mode" == "2" ]]; then
        break
    else
        echo "Invalid choice. Please press 1 or 2."
    fi
done

REPO_URL="https://github.com/USANJAY05/sql_notepad.git"

if [ "$mode" == "1" ]; then
    INSTALL_DIR="$HOME/.ipython/sql_notepad"
    BIN_DIR="$HOME/.local/bin"
    echo "Mode: Global Install"
else
    INSTALL_DIR="$PWD/sql_notepad"
    echo "Mode: Local Testing"
fi

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

if [ "$mode" == "1" ]; then
    echo "Setting up global 'mysql' command..."
    mkdir -p "$BIN_DIR"
    cat > "$BIN_DIR/mysql" << 'EOF'
#!/bin/sh
exec "$HOME/.ipython/sql_notepad/mysql" "$@"
EOF
    chmod +x "$BIN_DIR/mysql"

    # Add to PATH if necessary
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        echo "Adding $BIN_DIR to PATH in shell configuration..."
        
        # Check bash
        if [ -f "$HOME/.bashrc" ]; then
            if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.bashrc"; then
                echo -e '\n# SQL Notepad' >> "$HOME/.bashrc"
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
            fi
        fi
        
        # Check zsh
        if [ -f "$HOME/.zshrc" ]; then
            if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.zshrc"; then
                echo -e '\n# SQL Notepad' >> "$HOME/.zshrc"
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
            fi
        fi
        
        export PATH="$BIN_DIR:$PATH"
    fi
fi

echo "Starting setup..."
./mysql install

echo "========================================"
echo "Installation complete!"
if [ "$mode" == "1" ]; then
    echo "You can now run 'mysql start' from ANY directory."
    echo "Note: You may need to restart your terminal or run 'source ~/.zshrc' (or .bashrc) for the 'mysql' command to be available."
else
    echo "You can now run './mysql start' from inside the '$INSTALL_DIR' directory."
fi
echo "========================================"
