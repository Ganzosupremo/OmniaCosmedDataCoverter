@echo off
echo ===============================================
echo COSMED XML Data Converter
echo ===============================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo Virtual environment not found!
    echo Please run setup.bat first to install dependencies.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Check if arguments were provided
if "%~1"=="" (
    echo Usage: run_converter.bat [arguments for main.py]
    echo.
    echo Examples:
    echo   run_converter.bat test_files --export selected
    echo   run_converter.bat "C:\Data\CPET" results.xlsx --export max --verbose
    echo   run_converter.bat data_folder --list
    echo.
    echo For full help, run:
    echo   run_converter.bat --help
    echo.
    pause
    exit /b 0
)

REM Run the main script with all arguments
python main.py %*

REM Keep window open if there was an error
if %errorlevel% neq 0 (
    echo.
    echo Script finished with errors. Press any key to close.
    pause >nul
)
