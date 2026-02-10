# Migration from CSV to JSON

## What Changed?

The scraper now saves data as **JSON** instead of CSV. This is a better choice for web applications!

## Why JSON is Better

| Feature | CSV | JSON | Winner |
|---------|-----|------|--------|
| **Browser Loading** | ❌ Requires parsing | ✅ Native support | JSON |
| **CORS Issues** | ❌ Yes (needs server) | ✅ Can work with file:// | JSON |
| **Data Types** | ❌ Everything is string | ✅ Numbers, booleans, etc. | JSON |
| **File Size** | ⚠️ Larger | ✅ Smaller | JSON |
| **Parsing Speed** | ❌ Slow (custom parser) | ✅ Fast (built-in) | JSON |
| **Integration** | ⚠️ Manual work | ✅ Direct use | JSON |
| **Human Readable** | ✅ Yes | ✅ Yes | Tie |

## What You Need to Do

### Nothing! 🎉

The changes are automatic:

1. **Run the scraper** as usual:
   ```bash
   python main.py
   ```

2. **View products** as usual:
   ```bash
   python serve.py
   # or
   view_products.bat
   ```

3. **Everything works** - the server automatically finds the latest JSON file!

## File Changes

### Before (CSV)
```
aliexpress_products_20260210_102229.csv
aliexpress_products_top_rated_20260210_102229.csv
```

### After (JSON)
```
aliexpress_products_20260210_102229.json
aliexpress_products_top_rated_20260210_102229.json
products.json  ← Auto-created symlink to latest
```

## Code Changes

### Python (main.py)
- Changed from `import csv` to `import json`
- Replaced `save_to_csv()` with `save_to_json()`
- Simplified saving logic (no need for headers, columns, etc.)

### HTML (products_display.html)
- Changed from `fetch().text()` + CSV parsing to `fetch().json()`
- Removed 30+ lines of CSV parsing code
- Faster loading, cleaner code

### Server (serve.py)
- Added auto-detection of latest JSON file
- Creates `products.json` symlink automatically
- Shows which file is being used

## Benefits You'll Notice

1. **Faster Loading**: JSON loads instantly in the browser
2. **No More Parsing Errors**: Native JSON support = no bugs
3. **Smaller Files**: JSON is more compact than CSV
4. **Better Integration**: Easy to use with other tools/APIs
5. **Type Safety**: Numbers are numbers, not strings

## Old CSV Files

Your old CSV files (if any) are not deleted. You can:
- Keep them for reference
- Delete them if you don't need them
- Ignore them (they won't affect anything)

The scraper will only generate JSON files from now on.

## Technical Details

### JSON Structure
```json
[
  {
    "search_term": "best rated",
    "title": "Product Name",
    "price": "$19.99",
    "numeric_price": 19.99,
    "link": "https://...",
    "rating": "4.8",
    "numeric_rating": 4.8,
    "sold": "1000+ sold",
    "discount": "-50%",
    "image_url": "https://...",
    "scraped_at": "2026-02-10 10:22:29"
  },
  ...
]
```

### Loading in HTML
```javascript
// Before (CSV) - Complex
const response = await fetch('file.csv');
const text = await response.text();
const lines = text.split('\n');
// ... 30+ lines of parsing code ...

// After (JSON) - Simple!
const response = await fetch('file.json');
const products = await response.json();
// Done! ✅
```

## Questions?

### Can I still export to CSV?
Yes! You can easily convert JSON to CSV using:
- Python: `pandas.read_json('file.json').to_csv('file.csv')`
- Online tools: json2csv.com
- Excel: Can import JSON directly

### Will old scraped data work?
The HTML viewer only works with JSON files. Run the scraper once to generate new data.

### Can I use both formats?
The scraper only generates JSON now. If you need CSV, convert the JSON file.

## Summary

✅ **Better performance**  
✅ **Easier to use**  
✅ **No breaking changes for users**  
✅ **Automatic migration**  
✅ **More professional**  

You don't need to change anything in how you use the scraper. Just run it and enjoy the improvements!
