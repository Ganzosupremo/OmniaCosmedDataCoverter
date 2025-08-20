#!/bin/bash

echo ""
echo "===================================="
echo "  COSMED Converter - Advanced GUI"
echo "===================================="
echo ""
echo "Starting the advanced GUI application..."
echo ""

# Change to the script directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "Using system Python..."
fi

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "Error: Python not found. Please install Python 3.8 or higher."
    exit 1
fi

# Use python3 if available, otherwise use python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

# Run the advanced GUI application
echo "Launching advanced GUI..."
$PYTHON_CMD advanced_gui.py

# Check if the command was successful
if [ $? -ne 0 ]; then
    echo ""
    echo "An error occurred. Please check the error message above."
    echo "Press Enter to exit."
    read
fi
