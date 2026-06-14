#!/usr/bin/env python3
import os
import sys
import subprocess

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    install_script = os.path.join(script_dir, "install.py")
    
    # If no arguments provided, default to "start"
    args = sys.argv[1:]
    if not args:
        args = ["start"]
        
    cmd = [sys.executable, install_script] + args
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        sys.exit(1)

if __name__ == "__main__":
    main()
