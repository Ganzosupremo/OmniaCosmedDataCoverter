#!/bin/bash

echo "==============================================="
echo "COSMED XML Data Converter"
echo "==============================================="
echo

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found!"
    echo "Please run ./setup.sh first to install dependencies."
    echo
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if arguments were provided
if [ $# -eq 0 ]; then
    echo "Usage: ./run_converter.sh [arguments for main.py]"
    echo
    echo "Examples:"
    echo "  ./run_converter.sh test_files --export selected"
    echo "  ./run_converter.sh \"/home/user/CPET_Data\" results.xlsx --export max --verbose"
    echo "  ./run_converter.sh data_folder --list"
    echo
    echo "For full help, run:"
    echo "  ./run_converter.sh --help"
    echo
    exit 0
fi

# Run the main script with all arguments
python main.py "$@"
