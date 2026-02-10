#!/usr/bin/env python3
"""
AliExpress Top-Rated Product Scraper using SeleniumBase - JSON Output
Saves scraped products to JSON files for easy web integration.
"""

import time
import random
import signal
import sys
import re
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from seleniumbase import SB
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

# Fix Windows console encoding for emoji/special chars
if sys.platform == "win32":
    import io
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass  # If this fails, continue anyway

print("DEBUG: Imports completed, starting configuration...", flush=True)

# =============================================================================
# CONFIGURATION SETTINGS
# =============================================================================

# Proxy Settings
USE_PROXY = False  # Changed to False for testing - set to True once working
PROXY_LIST = [
    "p.webshare.io:80:hrkysyyr-3:1fi3bt0q1owh",
    "p.webshare.io:80:hrkysyyr-2:1fi3bt0q1owh",
]

# Browser Behavior Settings
ROTATE_USER_AGENTS = True
ADD_RANDOM_DELAYS = True
SIMULATE_HUMAN_BEHAVIOR = True
HEADLESS_MODE = True

# User Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
]

# Timing Settings
MIN_DELAY_BETWEEN_SEARCHES = 5
MAX_DELAY_BETWEEN_SEARCHES = 10
MIN_DELAY_BETWEEN_PRODUCTS = 0.1
MAX_DELAY_BETWEEN_PRODUCTS = 0.8
CAPTCHA_RETRY_DELAY = 5

# Product Filtering Settings
MIN_RATING_THRESHOLD = 4.0
MAX_SEARCH_TERMS = 2  # Reduced for testing - increase once working

# Browser Window Settings
WINDOW_WIDTH_MIN = 1200
WINDOW_WIDTH_MAX = 1920
WINDOW_HEIGHT_MIN = 800
WINDOW_HEIGHT_MAX = 1080

# Retry Settings
MAX_RETRIES_PER_SEARCH = 3
MAX_SSL_RETRIES = 3

# JSON Output Settings
JSON_OUTPUT_DIR = "."
JSON_FILENAME_PREFIX = "aliexpress_products"

# Search Terms
SEARCH_TERMS = [
    "best rated", "top rated", "highly rated", "popular", "trending",
    "best seller", "hot sale", "recommended", "trending products",
    "popular items", "best selling", "hot products", "trending items",
    "popular products", "best items", "hot items", "trending goods",
    "popular goods", "best goods", "hot goods", "trending merchandise",
]

should_stop = False
min_rating_threshold = MIN_RATING_THRESHOLD
top_rated_products: List[Dict[str, Any]] = []
all_products: List[Dict[str, Any]] = []


def signal_handler(signum, frame):
    global should_stop
    print("\n⚠️  Stopping script gracefully... finishing current term…")
    should_stop = True


def get_json_path() -> str:
    """Generate JSON file path with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(JSON_OUTPUT_DIR, f"{JSON_FILENAME_PREFIX}_{timestamp}.json")


def save_to_json(data: List[Dict[str, Any]], filepath: Optional[str] = None) -> None:
    """Save product data to JSON file."""
    if not data:
        print("⚠️  No data to save")
        return

    if filepath is None:
        filepath = get_json_path()

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(data)} products to {filepath}")
    except Exception as e:
        print(f"⚠️  Error saving to JSON: {e}")


def get_random_proxy() -> Optional[str]:
    """Get a random proxy from the list."""
    if USE_PROXY and PROXY_LIST:
        proxy = random.choice(PROXY_LIST)
        proxy_parts = proxy.split(":")
        if len(proxy_parts) == 4:
            proxy_host = proxy_parts[0]
            proxy_port = proxy_parts[1]
            proxy_user = proxy_parts[2]
            proxy_pass = proxy_parts[3]
            # SeleniumBase proxy format: http://username:password@host:port
            return f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
    return None


def get_random_user_agent() -> str:
    """Get a random user agent."""
    if ROTATE_USER_AGENTS:
        return random.choice(USER_AGENTS)
    return USER_AGENTS[0]


def delay(a=2, b=5):
    """Add random delay."""
    time.sleep(random.uniform(a, b))


def extract_numeric_rating(rating_str: str) -> float:
    """Extract numeric rating from string."""
    if not rating_str or rating_str == "N/A":
        return 0.0
    rating_clean = re.sub(r"[^\d.]", "", rating_str)
    try:
        return float(rating_clean)
    except ValueError:
        return 0.0


def extract_numeric_price(price_str: str) -> float:
    """Extract numeric price from string."""
    if not price_str or price_str == "N/A":
        return 0.0
    price_clean = re.sub(r"[^\d.,]", "", price_str)
    if "," in price_clean and "." in price_clean:
        price_clean = price_clean.replace(",", "")
    elif "," in price_clean:
        parts = price_clean.split(",")
        if len(parts[-1]) == 2:
            price_clean = "".join(parts[:-1]) + "." + parts[-1]
        else:
            price_clean = price_clean.replace(",", "")
    try:
        return float(price_clean)
    except ValueError:
        return 0.0


def extract_product_data(sb, card, keyword: str) -> Optional[Dict[str, Any]]:
    """Extract product data using SeleniumBase."""
    try:
        # Get all text from the card for parsing
        card_text = card.text.strip()
        lines = [line.strip() for line in card_text.split('\n') if line.strip()]
        
        title = "N/A"
        try:
            # Try to find the actual product title link first
            title_element = card.find_element(
                By.CSS_SELECTOR,
                "a[href*='/item/'] h3, a[href*='/item/'] h1, a[href*='/item/'] h2, a[href*='/item/']",
            )
            title_text = title_element.text.strip()
            # Split by newline and take only the first line (actual title)
            if title_text:
                title = title_text.split('\n')[0].strip()
        except Exception:
            # Try alternative selectors - get only the first line
            try:
                title_element = card.find_element(By.CSS_SELECTOR, "h3, h2, h1")
                title_text = title_element.text.strip()
                if title_text:
                    title = title_text.split('\n')[0].strip()
            except Exception:
                # Fallback: use first line from card text
                if lines:
                    title = lines[0]

        link = "N/A"
        try:
            link_element = card.find_element(
                By.CSS_SELECTOR,
                "a[href*='/item/'], a[href*='aliexpress.com/item']",
            )
            link = link_element.get_attribute("href") or "N/A"
        except Exception:
            pass

        price = "N/A"
        try:
            # Parse price from card text - look for currency symbols
            for line in lines:
                # Check if line contains currency and looks like a price
                if any(curr in line for curr in ['￡', '£', '$', '€', 'USD', 'GBP']) and any(c.isdigit() for c in line):
                    # Avoid lines with multiple prices (like "￡42.99 ￡164.3")
                    # Take the first price which is usually the current price
                    price_match = re.search(r'[￡£$€]\s*\d+\.?\d*', line)
                    if price_match:
                        price = price_match.group(0)
                        break
        except Exception:
            pass

        rating = "N/A"
        try:
            # Parse rating from card text - look for numbers between 0-5
            for line in lines:
                # Look for standalone numbers that could be ratings
                rating_match = re.search(r'^(\d+\.?\d*)$', line)
                if rating_match:
                    rating_val = float(rating_match.group(1))
                    if 0 <= rating_val <= 5:
                        rating = line
                        break
        except Exception:
            pass

        sold = "N/A"
        try:
            # Parse sold from card text
            for line in lines:
                if 'sold' in line.lower():
                    sold = line
                    break
        except Exception:
            pass

        discount = "N/A"
        try:
            # Parse discount from card text - look for percentage
            for line in lines:
                if '%' in line and '-' in line:
                    discount = line
                    break
        except Exception:
            pass

        image_url = ""
        try:
            img_element = card.find_element(By.CSS_SELECTOR, "img")
            image_url = (
                img_element.get_attribute("src") or img_element.get_attribute("data-src") or ""
            )
        except Exception:
            pass

        numeric_rating = extract_numeric_rating(rating)
        numeric_price = extract_numeric_price(price)

        return {
            "search_term": keyword,
            "title": title,
            "price": price,
            "numeric_price": numeric_price,
            "link": link,
            "rating": rating,
            "numeric_rating": numeric_rating,
            "sold": sold,
            "discount": discount,
            "image_url": image_url or "",
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    except Exception as e:
        print(f"⚠️  Error extracting product data: {e}")
        return None


def is_captcha_page(sb) -> bool:
    """Check if the current page is a captcha page."""
    try:
        if sb.driver is None:
            print("⚠️  Driver is None in captcha check")
            return False

        try:
            current_url = sb.driver.current_url.lower()
            captcha_indicators = [
                "captcha", "verify", "security", "robot", "human",
                "challenge", "verification", "check",
            ]
            if any(indicator in current_url for indicator in captcha_indicators):
                print("🚫 Captcha detected in URL")
                return True
        except Exception as e:
            print(f"⚠️  Error checking URL for captcha: {e}")
            return False

        captcha_selectors = [
            'span[id="nc_1_n1z"]',
            'div[id="nc_1__scale_text"]',
            'span[class*="btn_slide"]',
            'div[class*="scale_text"]',
            'div[class*="slidetounlock"]',
            'div[class*="captcha"]',
            'div[class*="verify"]',
            'div[class*="security"]',
            'iframe[src*="captcha"]',
            'form[action*="captcha"]',
            'input[name*="captcha"]',
            'div[class*="robot"]',
            'div[class*="human"]',
            'div[class*="nc_wrapper"]',
            'span[class*="nc_iconfont"]',
            'div[class*="slider"]',
        ]

        for selector in captcha_selectors:
            try:
                if sb.driver.find_element(By.CSS_SELECTOR, selector):
                    print(f"🚫 Captcha element detected: {selector}")
                    return True
            except NoSuchElementException:
                continue
            except Exception as e:
                print(f"⚠️  Error checking selector {selector}: {e}")
                continue

        try:
            page_text = sb.driver.page_source.lower()
            captcha_texts = [
                "verify you are human",
                "prove you are human",
                "security check",
                "captcha",
                "robot verification",
                "human verification",
                "滑块",
                "slide",
                "verification",
                "slide to verify",
                "please slide to verify",
            ]
            if any(text in page_text for text in captcha_texts):
                print("🚫 Captcha text detected on page")
                return True
        except Exception as e:
            print(f"⚠️  Error checking page text for captcha: {e}")

        return False
    except Exception as e:
        print(f"⚠️  Error in captcha check: {e}")
        return False


def solve_slider_captcha_advanced(sb) -> bool:
    """Advanced slider captcha solving with multiple strategies."""
    try:
        print("🎯 Attempting advanced slider captcha solving...")

        slider_selectors = [
            'span[id="nc_1_n1z"]',
            'span[class*="btn_slide"]',
            'span[class*="nc_iconfont"]',
            'span[aria-label*="滑块"]',
            'span[aria-label*="slide"]',
            'span[class*="slider"]',
            'div[class*="slider"]',
            'span[id*="nc"]',
            'div[id*="nc"]',
            'div[class*="nc_wrapper"]',
            'div[class*="slider-button"]',
            'div[class*="slider-handle"]',
            'div[class*="slider-thumb"]',
            'div[class*="nc_scale"]',
            'div[class*="nc_scale_text"]',
        ]

        slider_element = None
        for selector in slider_selectors:
            try:
                elements = sb.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        slider_element = element
                        print(f"✅ Found slider element: {selector}")
                        sb.execute_script(
                            """
                            arguments[0].style.border = '3px solid red';
                            arguments[0].style.backgroundColor = 'yellow';
                            arguments[0].style.zIndex = '9999';
                        """,
                            slider_element,
                        )
                        break
                if slider_element:
                    break
            except Exception as e:
                print(f"⚠️  Error checking selector {selector}: {e}")
                continue

        if not slider_element:
            print("❌ No slider element found")
            try:
                clickable_elements = sb.driver.find_elements(
                    By.CSS_SELECTOR,
                    "div[class*='nc'], span[class*='nc'], div[class*='slider'], span[class*='slider']",
                )
                for elem in clickable_elements:
                    if elem.is_displayed() and elem.is_enabled():
                        slider_element = elem
                        print(f"✅ Found alternative slider element: {elem.get_attribute('class')}")
                        break
            except Exception as e:
                print(f"⚠️  Error finding alternative slider: {e}")
                if "stale element" in str(e).lower():
                    print("🔄 Stale element detected, refreshing page and retrying...")
                    sb.driver.refresh()
                    sb.sleep(3)
                    return solve_slider_captcha_advanced(sb)

            if not slider_element:
                return False

        track_selectors = [
            'div[id="nc_1__scale_text"]',
            'div[class*="scale_text"]',
            'div[class*="slidetounlock"]',
            'div[class*="nc_wrapper"]',
            'div[class*="slider-track"]',
            'div[class*="nc_bg"]',
            'div[class*="track"]',
            'div[class*="slider-container"]',
            'div[class*="nc_scale"]',
            'div[class*="nc_scale_text"]',
        ]

        drag_distance = 300
        track_found = False

        for selector in track_selectors:
            try:
                track_elements = sb.driver.find_elements(By.CSS_SELECTOR, selector)
                for track_element in track_elements:
                    if track_element.is_displayed():
                        track_size = track_element.size
                        slider_size = slider_element.size
                        track_location = track_element.location
                        slider_location = slider_element.location
                        track_end_x = track_location["x"] + track_size["width"]
                        slider_center_x = slider_location["x"] + slider_size["width"] / 2
                        calculated_distance = track_end_x - slider_center_x + 20
                        if calculated_distance > 0:
                            drag_distance = calculated_distance
                            track_found = True
                            print(f"📏 Calculated drag distance: {drag_distance}px (with safety margin)")
                            break
                if track_found:
                    break
            except Exception as e:
                print(f"⚠️  Error calculating distance for {selector}: {e}")
                continue

        if not track_found:
            try:
                page_width = sb.execute_script("return window.innerWidth;")
                estimated_distance = min(page_width * 0.6, 400)
                drag_distance = estimated_distance
                print(f"📏 Using estimated drag distance: {drag_distance}px")
            except Exception:
                print(f"⚠️  Using default drag distance: {drag_distance}px")

        print("🔄 Performing single smooth slider movement...")

        try:
            slider_location = slider_element.location
            slider_size = slider_element.size
            start_x = slider_location["x"] + slider_size["width"] / 2
            start_y = slider_location["y"] + slider_size["height"] / 2

            actions = ActionChains(sb.driver)
            actions.move_to_element(slider_element).perform()
            sb.sleep(0.5)
            actions.click_and_hold(slider_element).perform()
            sb.sleep(0.2)

            print(f"🚀 Performing single smooth slider movement: {drag_distance}px...")
            y_offset = random.uniform(-1, 1)
            actions.move_by_offset(drag_distance, y_offset).perform()
            sb.sleep(0.1)
            print("💪 Final push: 5px")
            actions.move_by_offset(5, 0).perform()
            sb.sleep(0.2)
            actions.release().perform()
            sb.sleep(2)

            try:
                current_location = slider_element.location
                track_elements = sb.driver.find_elements(
                    By.CSS_SELECTOR,
                    'div[class*="nc_wrapper"], div[class*="slider"], div[class*="track"]',
                )
                if track_elements:
                    track_element = track_elements[0]
                    track_location = track_element.location
                    track_size = track_element.size
                    track_end_x = track_location["x"] + track_size["width"]
                    if current_location["x"] < track_end_x - 50:
                        print("🔄 Slider not at end, making final push...")
                        actions = ActionChains(sb.driver)
                        actions.click_and_hold(slider_element).perform()
                        actions.move_by_offset(50, 0).perform()
                        actions.release().perform()
                        sb.sleep(1)
            except Exception as e:
                print(f"⚠️  Position verification failed: {e}")

            success_selectors = [
                'div[class*="success"]',
                'div[class*="verified"]',
                'div[class*="complete"]',
                'span[class*="success"]',
            ]

            print("⏳ Waiting for verification result...")
            sb.sleep(2)

            for selector in success_selectors:
                try:
                    if sb.driver.find_element(By.CSS_SELECTOR, selector):
                        print("✅ Slider captcha appears to be solved")
                        return True
                except NoSuchElementException:
                    continue

            text_success_indicators = [
                "//div[contains(text(), '验证成功')]",
                "//div[contains(text(), 'Success')]",
                "//div[contains(text(), 'Verified')]",
                "//div[contains(text(), '完成')]",
                "//div[contains(text(), '通过')]",
                "//span[contains(text(), '验证成功')]",
                "//span[contains(text(), 'Success')]",
                "//span[contains(text(), 'Verified')]",
            ]

            for xpath in text_success_indicators:
                try:
                    if sb.driver.find_element(By.XPATH, xpath):
                        print(f"✅ Found success indicator: {xpath}")
                        return True
                except NoSuchElementException:
                    continue

            try:
                if not slider_element.is_displayed():
                    print("✅ Slider no longer visible - likely successful")
                    return True
            except Exception:
                pass

            try:
                scale_text = sb.driver.find_element(By.CSS_SELECTOR, 'div[id="nc_1__scale_text"]')
                text_content = scale_text.text
                if "SLIDE" not in text_content or "verify" not in text_content.lower():
                    print(f"✅ Slider text changed to: {text_content} - likely successful")
                    return True
            except NoSuchElementException:
                pass

            if not is_captcha_page(sb):
                print("✅ No longer on captcha page - likely successful")
                return True

            print("⚠️  Slider movement completed but success not confirmed")
            return False

        except Exception as e:
            print(f"⚠️  Error during slider movement: {e}")
            return False

    except Exception as e:
        print(f"⚠️  Error in advanced slider captcha solving: {e}")
        return False


def handle_captcha(sb) -> bool:
    """Handle captcha with comprehensive solving strategies."""
    print("🛡️  Handling captcha...")

    if solve_slider_captcha_advanced(sb):
        print("✅ Captcha solved successfully")
        return True

    print("🔄 Refreshing page...")
    sb.driver.refresh()
    sb.sleep(3)

    if not is_captcha_page(sb):
        print("✅ Captcha resolved after refresh")
        return True

    print("🧹 Clearing cookies...")
    try:
        sb.driver.delete_all_cookies()
        sb.driver.refresh()
        sb.sleep(3)
        if not is_captcha_page(sb):
            print("✅ Captcha resolved after clearing cookies")
            return True
    except Exception as e:
        print(f"⚠️  Cookie clearing failed: {e}")

    if is_captcha_page(sb):
        print("🔄 Trying slider captcha again after refresh...")
        if solve_slider_captcha_advanced(sb):
            print("✅ Captcha solved on second attempt")
            return True

    print("❌ All captcha solving strategies failed")
    return False


def simulate_human_behavior(sb) -> None:
    """Simulate human-like browsing behavior."""
    if not SIMULATE_HUMAN_BEHAVIOR:
        return
    try:
        print("🤖 Simulating human behavior...")
        scroll_amount = random.randint(100, 500)
        sb.execute_script(f"window.scrollBy(0, {scroll_amount})")
        sb.sleep(random.uniform(0.5, 1.5))
        back_scroll = random.randint(50, 200)
        sb.execute_script(f"window.scrollBy(0, -{back_scroll})")
        sb.sleep(random.uniform(0.3, 0.8))
        print("✅ Human behavior simulation completed")
    except Exception as e:
        print(f"⚠️  Error in human behavior simulation: {e}")


def main() -> None:
    signal.signal(signal.SIGINT, signal_handler)

    print("=" * 60, flush=True)
    print("🚀 ALIEXPRESS SCRAPER WITH SELENIUMBASE (CSV OUTPUT)", flush=True)
    print("=" * 60, flush=True)
    print(f"🎯 Min rating threshold: {min_rating_threshold}", flush=True)
    print(f"🧾 Search terms: {len(SEARCH_TERMS[:MAX_SEARCH_TERMS])}", flush=True)
    if USE_PROXY:
        print(f"🌐 Proxy rotation enabled with {len(PROXY_LIST)} proxies", flush=True)
    if SIMULATE_HUMAN_BEHAVIOR:
        print("🤖 Human behavior simulation enabled", flush=True)
    print(f"📁 JSON output: {JSON_OUTPUT_DIR}", flush=True)
    print("=" * 60, flush=True)

    search_terms = SEARCH_TERMS[:MAX_SEARCH_TERMS]
    json_path = get_json_path()

    for i, keyword in enumerate(search_terms, start=1):
        if should_stop:
            print("⏹️  Interrupted by user.")
            break

        print(f"\n🔍 {i}/{len(search_terms)} Searching: {keyword}", flush=True)

        proxy = get_random_proxy()
        if proxy:
            print(f"🌐 Using proxy: {proxy.split('@')[1] if '@' in proxy else proxy}", flush=True)

        if i > 1:
            print(f"⏳ Waiting {MIN_DELAY_BETWEEN_SEARCHES}-{MAX_DELAY_BETWEEN_SEARCHES}s before next search...", flush=True)
            delay(MIN_DELAY_BETWEEN_SEARCHES, MAX_DELAY_BETWEEN_SEARCHES)

        url = f"https://www.aliexpress.com/wholesale?SearchText={keyword.replace(' ', '+')}"

        try:
            print(f"🚀 Initializing browser (headless={HEADLESS_MODE}, proxy={bool(proxy)})...", flush=True)
            try:
                with SB(
                    uc=True,
                    proxy=proxy,
                    headless=HEADLESS_MODE,
                    window_size=f"{random.randint(WINDOW_WIDTH_MIN, WINDOW_WIDTH_MAX)},{random.randint(WINDOW_HEIGHT_MIN, WINDOW_HEIGHT_MAX)}",
                ) as sb:
                    print(f"✅ Browser initialized successfully", flush=True)

                    print(f"🌐 Loading: {url}", flush=True)
                    sb.driver.get(url)
                    print(f"✅ Page loaded, waiting 3s...", flush=True)
                    sb.sleep(3)

                    if is_captcha_page(sb):
                        print("🚫 Captcha detected! Attempting to solve...", flush=True)
                        if handle_captcha(sb):
                            print("✅ Captcha resolved, continuing...", flush=True)
                            sb.sleep(2)
                        else:
                            print("❌ Failed to solve captcha, skipping this keyword", flush=True)
                            continue

                    simulate_human_behavior(sb)

                    print("📜 Scrolling to load more products...", flush=True)
                    for scroll_num in range(5):
                        scroll_amount = random.randint(400, 600)
                        sb.execute_script(f"window.scrollBy(0, {scroll_amount})")
                        sb.sleep(random.uniform(1.5, 2.5))
                        if random.random() < 0.2:
                            back_scroll = random.randint(50, 150)
                            sb.execute_script(f"window.scrollBy(0, -{back_scroll})")
                            sb.sleep(random.uniform(0.5, 1))

                    cards = sb.driver.find_elements(
                        By.CSS_SELECTOR,
                        "div[data-tticheck='true'], div[class*='product'], div[class*='item'], div[class*='card']",
                    )
                    print(f"✅ Found {len(cards)} products", flush=True)

                    if not cards:
                        print("❌ No products found", flush=True)
                        continue

                    term_products: List[Dict[str, Any]] = []
                    successful_extractions = 0
                    top_rated_count = 0

                    max_products_to_process = min(len(cards), 50)
                    print(f"🔄 Processing {max_products_to_process} products...", flush=True)

                    for j, card in enumerate(cards[:max_products_to_process]):
                        try:
                            product_data = extract_product_data(sb, card, keyword)

                            if (
                                product_data
                                and product_data.get("title")
                                and product_data.get("title") != "N/A"
                            ):
                                if product_data["numeric_rating"] >= min_rating_threshold:
                                    top_rated_products.append(product_data)
                                    top_rated_count += 1

                                term_products.append(product_data)
                                successful_extractions += 1
                            else:
                                # Debug: show why product was rejected
                                if j < 3:  # Only show first 3 for debugging
                                    print(f"⚠️  Product {j+1} rejected: title={product_data.get('title') if product_data else 'None'}", flush=True)

                            if (j + 1) % 10 == 0:
                                print(f"📊 Processed {j + 1}/{max_products_to_process} products... (extracted: {successful_extractions})", flush=True)

                            if j < max_products_to_process - 1:
                                sb.sleep(random.uniform(0.05, 0.2))

                        except Exception as e:
                            print(f"⚠️  Error processing product {j + 1}: {e}", flush=True)
                            continue

                    print(f"✅ {successful_extractions} products extracted, {top_rated_count} passed threshold", flush=True)
                    all_products.extend(term_products)

                    # Save incrementally to JSON
                    if all_products:
                        save_to_json(all_products, filepath=json_path)

                    print(f"🎯 Overall progress: {i}/{len(search_terms)} keywords completed", flush=True)
                    print(f"📈 Total products: {len(all_products)}", flush=True)
                    print(f"⭐ Top-rated products: {len(top_rated_products)}", flush=True)
                    print("-" * 50, flush=True)

            except Exception as browser_error:
                print(f"⚠️  Browser initialization error: {browser_error}", flush=True)
                import traceback
                traceback.print_exc()
                continue

        except Exception as e:
            print(f"⚠️  Error processing keyword '{keyword}': {e}", flush=True)
            import traceback
            traceback.print_exc()
            continue

    # Final save: top-rated only to a separate JSON if desired
    top_json_path = None
    if top_rated_products:
        top_json_path = os.path.join(
            JSON_OUTPUT_DIR,
            f"{JSON_FILENAME_PREFIX}_top_rated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        )
        save_to_json(top_rated_products, filepath=top_json_path)

    print(f"\n🎉 FINISHED! Total scraped: {len(all_products)}, Top-rated: {len(top_rated_products)}")
    print("=" * 60)
    print("📊 FINAL REPORT")
    print("=" * 60)
    print(f"✅ Keywords processed: {len(search_terms)}")
    print(f"📈 Total products collected: {len(all_products)}")
    print(f"⭐ Top-rated products (≥{MIN_RATING_THRESHOLD}): {len(top_rated_products)}")
    print(f"🎯 Success rate: {(len(top_rated_products) / max(len(all_products), 1) * 100):.1f}% top-rated products")
    print(f"📁 All products JSON: {json_path}")
    if top_json_path:
        print(f"📁 Top-rated JSON: {top_json_path}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        print("Starting script...", flush=True)
        main()
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)

