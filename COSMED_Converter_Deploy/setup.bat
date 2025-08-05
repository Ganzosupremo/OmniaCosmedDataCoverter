@echo off
echo ===============================================
echo COSMED XML Data Converter - Setup Script
echo ===============================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or newer from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found!
python --version

echo.
echo Creating virtual environment...
if exist ".venv" (
    echo Virtual environment already exists. Removing old one...
    rmdir /s /q ".venv"
)

python -m venv .venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Installing required packages...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)

echo.
echo ===============================================
echo Setup completed successfully!
echo ===============================================
echo.
echo To use the COSMED XML Data Converter:
echo.
echo 1. Open Command Prompt in this folder
echo 2. Run: .venv\Scripts\activate
echo 3. Run: python main.py --help
echo.
echo Or use the provided run scripts:
echo - run_converter.bat (Windows)
echo - run_converter.sh (Linux/Mac)
echo.
echo Example usage:
echo python main.py test_files --export selected
echo.
pause
