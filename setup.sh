#!/bin/bash

echo "========================================"
echo "AliExpress Product Scraper Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "[1/4] Python found"
python3 --version
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "[2/4] Virtual environment already exists"
else
    echo "[2/4] Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
fi
echo ""

# Activate virtual environment and install dependencies
echo "[3/4] Installing dependencies..."
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo ""

# Create config file if it doesn't exist
if [ -f "config.py" ]; then
    echo "[4/4] config.py already exists"
else
    echo "[4/4] Creating config.py from example..."
    cp config.example.py config.py
    echo "NOTE: Please edit config.py to customize your settings"
fi
echo ""

echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "To run the scraper:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run the scraper: python main.py"
echo "  3. View results: Open products_display.html"
echo ""
echo "Optional: Edit config.py to customize settings"
echo ""
