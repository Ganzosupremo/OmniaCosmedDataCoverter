#!/bin/bash

echo "==============================================="
echo "COSMED XML Data Converter - Setup Script"
echo "==============================================="
echo

echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or newer:"
    echo "- Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    echo "- macOS: brew install python3 (or download from https://python.org)"
    echo "- CentOS/RHEL: sudo yum install python3 python3-pip"
    exit 1
fi

echo "Python found!"
python3 --version

echo
echo "Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "Virtual environment already exists. Removing old one..."
    rm -rf .venv
fi

python3 -m venv .venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    echo "You may need to install python3-venv:"
    echo "sudo apt install python3-venv"
    exit 1
fi

echo
echo "Activating virtual environment..."
source .venv/bin/activate

echo
echo "Installing required packages..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install packages"
    exit 1
fi

echo
echo "==============================================="
echo "Setup completed successfully!"
echo "==============================================="
echo
echo "To use the COSMED XML Data Converter:"
echo
echo "1. Open terminal in this folder"
echo "2. Run: source .venv/bin/activate"
echo "3. Run: python main.py --help"
echo
echo "Or use the provided run scripts:"
echo "- ./run_converter.sh (Linux/Mac)"
echo "- run_converter.bat (Windows)"
echo
echo "Example usage:"
echo "python main.py test_files --export selected"
echo

# Make run script executable
chmod +x run_converter.sh
