@echo off
echo ========================================
echo AliExpress Product Scraper Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Python found
python --version
echo.

REM Check if virtual environment exists
if exist "venv\" (
    echo [2/4] Virtual environment already exists
) else (
    echo [2/4] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)
echo.

REM Activate virtual environment and install dependencies
echo [3/4] Installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

REM Create config file if it doesn't exist
if exist "config.py" (
    echo [4/4] config.py already exists
) else (
    echo [4/4] Creating config.py from example...
    copy config.example.py config.py
    echo NOTE: Please edit config.py to customize your settings
)
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To run the scraper:
echo   1. Activate virtual environment: venv\Scripts\activate
echo   2. Run the scraper: python main.py
echo   3. View results: Open products_display.html
echo.
echo Optional: Edit config.py to customize settings
echo.
pause
