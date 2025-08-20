@echo off
echo.
echo ====================================
echo   COSMED Converter - Advanced GUI
echo ====================================
echo.
echo Starting the advanced GUI application...
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo Using system Python...
)

REM Run the advanced GUI application
echo Launching advanced GUI...
python advanced_gui.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit.
    pause >nul
)
