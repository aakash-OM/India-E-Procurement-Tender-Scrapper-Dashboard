"""
GeM Portal HTML Debugger
Run this FIRST to capture actual page source & find correct CSS selectors.
Output: gem_debug_output.html  (open in browser to inspect)
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

TEST_KEYWORD = "transformer"   # broad keyword to guarantee results

def main():
    opts = Options()
    # HEADLESS = FALSE so you can watch what loads
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=opts
    )

    url = f"https://bidplus.gem.gov.in/all-bids?searchedBid={TEST_KEYWORD}&page=1"
    print(f"Opening: {url}")
    driver.get(url)

    # Wait longer — GeM is JS heavy
    print("Waiting 8 seconds for JS to render...")
    time.sleep(8)

    page_source = driver.page_source

    # Save full HTML for inspection
    with open("gem_debug_output.html", "w", encoding="utf-8") as f:
        f.write(page_source)
    print("Full HTML saved to: gem_debug_output.html")

    # Print a 3000-char snippet to find real class names
    # Focus on the middle where bid cards usually appear
    mid = len(page_source) // 2
    snippet = page_source[mid - 1500 : mid + 1500]
    print("\n===== PAGE SOURCE SNIPPET (middle section) =====")
    print(snippet)
    print("================================================\n")

    # Try every possible selector and report which ones match
    selectors_to_try = [
        "#block_all_bids",
        ".block-bid-details",
        ".bid-details",
        ".bid_no_hover",
        "[id^='bid_']",
        ".card.mb-3",
        ".card",
        "div[id^='bid']",
        ".bidlist",
        ".bid-list",
        ".bid_list",
        ".tender-list",
        "table tr",
        ".table tbody tr",
        ".container .row .col",
        "div.row div.col-md",
    ]

    print("===== SELECTOR TEST RESULTS =====")
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(page_source, "html.parser")
    for sel in selectors_to_try:
        found = soup.select(sel)
        print(f"  {sel!r:<45} → {len(found)} elements")

    # Print all div IDs and class names found
    print("\n===== ALL DIV IDs (first 40) =====")
    divs_with_id = soup.find_all("div", id=True)[:40]
    for d in divs_with_id:
        print(f"  id={d['id']!r}  class={d.get('class', [])}")

    print("\n===== ALL UNIQUE CLASS NAMES ON DIVs =====")
    all_classes = set()
    for d in soup.find_all("div", class_=True):
        for c in d["class"]:
            all_classes.add(c)
    for c in sorted(all_classes):
        print(f"  .{c}")

    driver.quit()
    print("\nDone. Check gem_debug_output.html in your browser for full page HTML.")

if __name__ == "__main__":
    main()
