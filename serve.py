#!/usr/bin/env python3
"""
Simple HTTP server to view the products display HTML
Run this script and open http://localhost:8000 in your browser
"""

import http.server
import socketserver
import webbrowser
import os
import shutil
import glob
from pathlib import Path

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers to allow fetch requests
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

def find_latest_json():
    """Find the latest aliexpress_products JSON file and create a symlink."""
    json_files = glob.glob("aliexpress_products_*.json")
    if json_files:
        # Sort by modification time, get the latest
        latest = max(json_files, key=os.path.getmtime)
        
        # Create a copy as products.json for easy access
        try:
            shutil.copy2(latest, "products.json")
            print(f"📄 Using latest data file: {latest}")
            return True
        except Exception as e:
            print(f"⚠️  Could not create products.json: {e}")
            return False
    return False

def main():
    # Change to the script directory
    os.chdir(Path(__file__).parent)
    
    # Find and link latest JSON file
    if not find_latest_json():
        print("⚠️  No product JSON files found. Run 'python main.py' first to scrape products.")
        print("    Or make sure you have a 'products.json' or 'aliexpress_products_*.json' file.")
        print()
    
    Handler = MyHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}/products_display.html"
        print("=" * 60)
        print("🌐 Starting HTTP Server")
        print("=" * 60)
        print(f"📡 Server running at: http://localhost:{PORT}")
        print(f"📄 View products at: {url}")
        print("=" * 60)
        print("Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Try to open browser automatically
        try:
            print(f"\n🚀 Opening browser...")
            webbrowser.open(url)
        except Exception as e:
            print(f"⚠️  Could not open browser automatically: {e}")
            print(f"Please open {url} manually in your browser")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped")

if __name__ == "__main__":
    main()
