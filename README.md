# AliExpress Product Scraper

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production-brightgreen.svg)

A powerful web scraper for extracting top-rated products from AliExpress using SeleniumBase with undetected Chrome driver. The scraper saves data as JSON and includes a beautiful web viewer, advanced captcha handling, proxy rotation support, and human-like behavior simulation.

---

## Table of Contents

- [Quick Start](#-quick-start)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Output Format](#output-format)
- [Project Structure](#project-structure)
- [Features in Detail](#features-in-detail)
- [Troubleshooting](#troubleshooting)
- [Performance Tips](#performance-tips)
- [Legal Disclaimer](#legal-disclaimer)

---

## 🚀 Quick Start

### Step 1: Setup (One-time)

**Windows:**
```bash
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### Step 2: Run Scraper
```bash
python main.py
```

### Step 3: View Products
```bash
# Windows
view_products.bat

# Linux/Mac
./view_products.sh

# Or use Python directly
python serve.py
```

**Important**: Don't open `products_display.html` directly! Use the viewer scripts above to avoid CORS issues.

### Manual Setup

```bash
# 1. Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy config file (optional)
cp config.example.py config.py  # Linux/Mac
copy config.example.py config.py  # Windows

# 4. Run the scraper
python main.py

# 5. View results
python serve.py  # Starts web server and opens browser
# or double-click view_products.bat (Windows) / view_products.sh (Linux/Mac)
```

## Features

- ✅ **Undetected Chrome Driver**: Uses SeleniumBase's UC mode to avoid detection
- 🤖 **Smart Captcha Handling**: Automatically detects and solves slider captchas
- 🌐 **Proxy Support**: Rotate through multiple proxies to avoid rate limiting
- 🎭 **Human Behavior Simulation**: Mimics real user interactions with random scrolling and delays
- 📊 **JSON Export**: Saves all scraped data to JSON files for easy integration
- 🎨 **Beautiful HTML Display**: Includes a glassmorphism-styled product viewer
- ⭐ **Rating Filter**: Focus on highly-rated products (configurable threshold)
- 🔄 **Retry Logic**: Automatically retries failed requests

## Installation

### Prerequisites

- Python 3.8 or higher
- Chrome browser installed

### Setup

1. Clone or download this repository

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### Option 1: Using Config File (Recommended)

1. Copy the example config file:
```bash
copy config.example.py config.py  # Windows
# or
cp config.example.py config.py    # Linux/Mac
```

2. Edit `config.py` with your settings

### Option 2: Edit Main Script

Edit the configuration settings directly in `main.py`:

### Proxy Settings
```python
USE_PROXY = False  # Set to True to enable proxy rotation
PROXY_LIST = [
    "p.webshare.io:80:username:password",
    # Add more proxies as needed
]
```

### Scraping Settings
```python
MIN_RATING_THRESHOLD = 4.0  # Minimum product rating to collect
MAX_SEARCH_TERMS = 2  # Number of search terms to process
HEADLESS_MODE = True  # Run browser in headless mode
```

### Timing Settings
```python
MIN_DELAY_BETWEEN_SEARCHES = 5  # Seconds between searches
MAX_DELAY_BETWEEN_SEARCHES = 10
MIN_DELAY_BETWEEN_PRODUCTS = 0.1  # Seconds between product extractions
MAX_DELAY_BETWEEN_PRODUCTS = 0.8
```

## Usage

### Basic Usage

Run the scraper:
```bash
python main.py
```

The scraper will:
1. Process search terms from the configured list
2. Extract product information (title, price, rating, sold count, discount, image)
3. Save results to JSON files with timestamps
4. Generate two JSON files:
   - `aliexpress_products_YYYYMMDD_HHMMSS.json` - All products
   - `aliexpress_products_top_rated_YYYYMMDD_HHMMSS.json` - Only top-rated products

### Viewing Results

**Important**: Due to browser security restrictions, you need to serve the HTML file via HTTP (not open it directly).

**Option 1: Using the provided server script (Recommended)**
```bash
python serve.py
# or
python view_products.bat  # Windows
./view_products.sh        # Linux/Mac
```

**Option 2: Using Python's built-in server**
```bash
python -m http.server 8000
# Then open http://localhost:8000/products_display.html
```

**Note**: The viewer automatically loads the latest JSON file. No configuration needed!

The product viewer includes:
- Beautiful glassmorphism design
- Search and filter functionality
- Sort by price, rating, or discount
- Click any product to open on AliExpress

## Output Format

### JSON Structure
Each product is saved as a JSON object with the following fields:

```json
{
  "search_term": "best rated",
  "title": "Product Name",
  "price": "$19.99",
  "numeric_price": 19.99,
  "link": "https://www.aliexpress.com/item/...",
  "rating": "4.8",
  "numeric_rating": 4.8,
  "sold": "1000+ sold",
  "discount": "-50%",
  "image_url": "https://...",
  "scraped_at": "2026-02-10 10:22:29"
}
```

**Benefits of JSON:**
- ✅ Native JavaScript support (no parsing needed)
- ✅ Preserves data types (numbers stay as numbers)
- ✅ Easy to integrate with other tools
- ✅ Can be loaded directly in browser (no CORS issues with file://)
- ✅ More compact than CSV

## Project Structure

```
├── main.py                       # Main scraper script
├── products_display.html         # Product viewer with glassmorphism UI
├── serve.py                      # HTTP server for viewing products
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── .gitignore                    # Git ignore file
├── setup.bat                     # Windows setup script
├── setup.sh                      # Linux/Mac setup script
├── view_products.bat             # Windows viewer launcher
├── view_products.sh              # Linux/Mac viewer launcher
├── products.json                 # Latest products (auto-created)
└── aliexpress_products_*.json    # Generated JSON files with timestamps
```

## Screenshots

### Product Display
The included HTML viewer features:
- Modern glassmorphism design with animated gradients
- Real-time search and filtering
- Sort by price, rating, or discount
- Responsive layout for all devices
- Click-to-open product links

## Features in Detail

### Captcha Handling
The scraper includes advanced captcha detection and solving:
- Detects various captcha types (slider, text-based)
- Attempts multiple solving strategies
- Automatically refreshes and retries on failure

### Human Behavior Simulation
To avoid detection, the scraper:
- Uses random delays between actions
- Simulates scrolling behavior
- Varies window sizes
- Rotates user agents

### Error Handling
- Graceful handling of network errors
- Automatic retry on SSL errors
- Continues processing even if individual products fail
- Detailed logging of all operations

## Troubleshooting

### Common Issues

**Issue**: Products not loading in HTML viewer
- **Solution**: Don't open the HTML file directly. Use the web server:
  ```bash
  python serve.py
  # or
  view_products.bat  # Windows
  ./view_products.sh # Linux/Mac
  ```

**Issue**: Captcha not being solved
- **Solution**: The scraper will automatically retry. If it consistently fails, try:
  - Disabling headless mode (`HEADLESS_MODE = False`)
  - Enabling proxy rotation
  - Increasing delays between requests

**Issue**: No products found in scraper
- **Solution**: 
  - Check your internet connection
  - Verify AliExpress is accessible in your region
  - Try different search terms

**Issue**: JSON file not found in viewer
- **Solution**: 
  - Run the scraper first: `python main.py`
  - Make sure `products.json` or `aliexpress_products_*.json` exists
  - Use `python serve.py` which auto-detects the latest file

**Issue**: Browser driver errors
- **Solution**: SeleniumBase automatically manages drivers. If issues persist:
  ```bash
  pip install --upgrade seleniumbase
  ```

## Performance Tips

1. **Adjust delays**: Increase delays if you're getting blocked frequently
2. **Use proxies**: Enable proxy rotation for higher volume scraping
3. **Limit search terms**: Start with fewer search terms and increase gradually
4. **Monitor output**: Watch the console for errors and adjust settings accordingly

## Legal Disclaimer

This tool is for educational purposes only. When using this scraper:
- Respect AliExpress's Terms of Service
- Don't overload their servers with requests
- Use appropriate delays between requests
- Consider using proxies to distribute load
- Be aware of legal implications in your jurisdiction

## Support

For issues or questions:
1. Review the [Troubleshooting](#troubleshooting) section above
2. Check the [SeleniumBase documentation](https://seleniumbase.io/)
3. Verify your configuration settings match your requirements

---

**Note**: This scraper is designed to be respectful of server resources. Always use appropriate delays and consider the impact of your scraping activities.
