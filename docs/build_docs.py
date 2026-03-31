#!/usr/bin/env python3
"""
Simple script to build the django-lfs documentation.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {' '.join(cmd)}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        return False
    return True


def main():
    """Main build function."""
    docs_dir = Path(__file__).parent
    os.chdir(docs_dir)

    print("Building django-lfs documentation...")

    # Check if requirements are installed
    try:
        import sphinx

        print(f"Sphinx version: {sphinx.__version__}")
    except ImportError:
        print("Sphinx not found. Installing requirements...")
        if not run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]):
            print("Failed to install requirements")
            return 1

    # Clean previous build
    if Path("_build").exists():
        print("Cleaning previous build...")
        shutil.rmtree("_build")

    # Build HTML documentation
    print("Building HTML documentation...")
    if not run_command([sys.executable, "-m", "sphinx", "-b", "html", ".", "_build/html"]):
        print("Failed to build HTML documentation")
        return 1

    print("Documentation built successfully!")
    print(f"HTML files are in: {docs_dir / '_build' / 'html'}")
    print(f"Open {docs_dir / '_build' / 'html' / 'index.html'} in your browser to view the docs.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
