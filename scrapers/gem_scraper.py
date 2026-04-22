"""
GeM Portal Scraper – adapted from gem_bid_scraper_fast.py for dashboard integration.
Reports progress via a shared status dict instead of console prints.
"""

import time
import re
import io
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader

GEM_BASE = "https://bidplus.gem.gov.in"
AJAX_WAIT = 7
PAGE_NAV_WAIT = 5
PDF_TIMEOUT = 20
PARALLEL_PDF_WORKERS = 10

CARD_SECTOR_KEYWORDS = [
    "Power", "Energy", "Electric", "Vidyut", "Bijli",
    "Transco", "Genco", "Discom", "Grid", "Transmission",
    "Generation", "Distribution", "Railways", "Railway",
    "NTPC", "BHEL", "NHPC", "PGCIL", "NHAI", "Heavy Industries",
    "Uttar Pradesh", "Maharashtra", "Gujarat", "Punjab", "Haryana",
    "Karnataka", "West Bengal", "Jharkhand", "Chhattisgarh", "Bihar",
    "Madhya Pradesh", "Himachal", "Uttarakhand", "Jammu", "Delhi",
    "Rajasthan", "Andhra Pradesh", "Telangana", "Tamil Nadu", "Kerala",
    "Odisha", "Assam", "Patratu",
]

BLOCKED_KEYWORDS = [
    "Repair", "Repairing", "Maintenance", "Installation", "Operation",
    "Cleaning", "Housekeeping", "Facility Management", "Management Service",
    "Cab", "Taxi", "Hiring", "Vehicle", "Car Rental", "Bus Hiring",
    "SUV", "Mahindra", "Scorpio", "Bolero", "Maruti", "Suzuki",
    "Paint", "Zinc", "Resin", "Acid", "Chemical", "Housekeeping",
]

STATE_REGION_MAP = {
    "Uttar Pradesh": "North", "Haryana": "North", "Punjab": "North",
    "Rajasthan": "North", "Delhi": "North", "Himachal Pradesh": "North",
    "Uttarakhand": "North", "Jammu & Kashmir": "North",
    "Maharashtra": "West", "Gujarat": "West", "Goa": "West",
    "Karnataka": "South", "Telangana": "South", "Andhra Pradesh": "South",
    "Tamil Nadu": "South", "Kerala": "South",
    "West Bengal": "East", "Odisha": "East", "Bihar": "East", "Jharkhand": "East",
    "Madhya Pradesh": "Central", "Chhattisgarh": "Central",
    "Assam": "Northeast", "Manipur": "Northeast", "Meghalaya": "Northeast",
    "Mizoram": "Northeast", "Nagaland": "Northeast", "Tripura": "Northeast",
    "Arunachal Pradesh": "Northeast", "Sikkim": "Northeast",
}


def _make_driver(headless=True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    svc = ChromeService(ChromeDriverManager().install())
    return webdriver.Chrome(service=svc, options=opts)


def _scrape_cards(driver, keyword, max_pages, status, db):
    """Scrape bid cards from GeM for one keyword. Returns list of card dicts."""
    cards = []
    for page in range(1, max_pages + 1):
        if not status.get("active"):
            break
        url = f"{GEM_BASE}/all-bids?searchedBid={requests.utils.quote(keyword)}&page={page}"
        try:
            driver.get(url)
            WebDriverWait(driver, AJAX_WAIT + 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "bid_no_hover"))
            )
            time.sleep(AJAX_WAIT)
        except Exception:
            break

        soup = BeautifulSoup(driver.page_source, "lxml")
        bid_cards = soup.select("div.bid_no_hover")
        if not bid_cards:
            break

        for card in bid_cards:
            try:
                bid_no_el = card.select_one("a.bid_no_hover") or card.select_one("[id^='bid_no_']")
                if not bid_no_el:
                    continue
                bid_no = bid_no_el.get_text(strip=True)
                href = bid_no_el.get("href", "")
                bid_url = href if href.startswith("http") else GEM_BASE + href

                dept_el = card.select_one(".bidding_unit") or card.select_one(".dept")
                state_el = card.select_one(".state") or card.select_one(".location")
                cat_el = card.select_one(".item_cat") or card.select_one(".category")

                dept_text = dept_el.get_text(strip=True) if dept_el else ""
                state_text = state_el.get_text(strip=True) if state_el else ""
                cat_text = cat_el.get_text(strip=True) if cat_el else ""
                combined = f"{dept_text} {state_text}".lower()

                if not any(k.lower() in combined for k in CARD_SECTOR_KEYWORDS):
                    continue
                if db.bid_exists("gem", bid_no):
                    continue

                cards.append({
                    "bid_number": bid_no,
                    "bid_url":    bid_url,
                    "department": dept_text,
                    "state_text": state_text,
                    "item_category": cat_text,
                    "keyword_used": keyword,
                })
            except Exception:
                continue

        status["log"].append(f"[GeM] '{keyword}' page {page}: {len(bid_cards)} cards found")
        if len(bid_cards) < 10:
            break
    return cards


def _fetch_pdf_text(session, bid_url):
    """Download bid page, find PDF link, return extracted text."""
    try:
        r = session.get(bid_url, timeout=PDF_TIMEOUT)
        soup = BeautifulSoup(r.text, "lxml")
        pdf_link = None
        for a in soup.find_all("a", href=True):
            if ".pdf" in a["href"].lower():
                pdf_link = a["href"]
                if not pdf_link.startswith("http"):
                    pdf_link = GEM_BASE + pdf_link
                break
        if not pdf_link:
            return ""
        r2 = session.get(pdf_link, timeout=PDF_TIMEOUT)
        reader = PdfReader(io.BytesIO(r2.content))
        return " ".join(p.extract_text() or "" for p in reader.pages)
    except Exception:
        return ""


def _parse_pdf_text(text):
    """Extract structured fields from PDF text using regex."""
    def find(patterns):
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return ""

    org_name = find([
        r"Organisation\s*Name\s*[:\-]\s*(.+?)(?:\n|Dept|Ministry)",
        r"Name\s+of\s+Organisation\s*[:\-]\s*(.+?)(?:\n|Dept)",
    ])
    department = find([
        r"Department\s*[:\-]\s*(.+?)(?:\n|Ministry|State)",
        r"Dept\.\s*[:\-]\s*(.+?)(?:\n|Ministry|State)",
    ])
    ministry = find([
        r"Ministry\s*[:\-]\s*(.+?)(?:\n|Department|State)",
    ])
    item_cat = find([
        r"Item\s*Category\s*[:\-]\s*(.+?)(?:\n|Quantity|Estimated)",
    ])
    quantity = find([
        r"Quantity\s*[:\-]\s*(.+?)(?:\n|Estimated|Bid)",
    ])

    value = None
    for p in [
        r"Estimated\s*Value\s*[:\-]\s*(?:Rs\.?|INR|₹)?\s*([\d,]+(?:\.\d+)?)",
        r"Total\s*Estimated\s*Cost\s*[:\-]\s*(?:Rs\.?|INR|₹)?\s*([\d,]+(?:\.\d+)?)",
    ]:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            try:
                value = float(m.group(1).replace(",", ""))
                break
            except ValueError:
                pass

    start_date = find([
        r"Bid\s*Start\s*Date\s*[:\-]\s*(\d{2}[/-]\d{2}[/-]\d{4})",
        r"Start\s*Date\s*[:\-]\s*(\d{2}[/-]\d{2}[/-]\d{4})",
    ])
    end_date = find([
        r"Bid\s*End\s*Date\s*[:\-]\s*(\d{2}[/-]\d{2}[/-]\d{4})",
        r"End\s*Date\s*[:\-]\s*(\d{2}[/-]\d{2}[/-]\d{4})",
    ])

    return {
        "org_name":        org_name,
        "department":      department or ministry,
        "item_category":   item_cat,
        "quantity":        quantity,
        "estimated_value": value,
        "bid_start_date":  start_date,
        "bid_end_date":    end_date,
    }


def run_gem_scrape(keywords, target_orgs, max_pages, status, db, headless=True):
    """
    Main entry point for the GeM scraper.
    keywords: list of keyword strings to search
    target_orgs: list of org name substrings to accept (empty = accept all)
    max_pages: pages per keyword
    status: shared dict for progress reporting
    db: Database instance
    """
    driver = _make_driver(headless)
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    })

    total_saved = 0
    total_keywords = len(keywords)

    try:
        for kw_idx, keyword in enumerate(keywords):
            if not status.get("active"):
                break

            status.update({
                "current_portal":  "GeM",
                "current_keyword": keyword,
                "progress":        int((kw_idx / total_keywords) * 100),
            })
            status["log"].append(f"[GeM] Searching: '{keyword}'")

            try:
                cards = _scrape_cards(driver, keyword, max_pages, status, db)
            except Exception as e:
                status["log"].append(f"[GeM] Browser error on '{keyword}': {e}")
                try:
                    driver.quit()
                except Exception:
                    pass
                driver = _make_driver(headless)
                continue

            if not cards:
                continue

            status["log"].append(f"[GeM] '{keyword}': {len(cards)} candidate bids → downloading PDFs")

            def process_card(card):
                text = _fetch_pdf_text(session, card["bid_url"])
                parsed = _parse_pdf_text(text)

                if any(b.lower() in (parsed.get("item_category") or "").lower() for b in BLOCKED_KEYWORDS):
                    return None

                if target_orgs:
                    org = (parsed.get("org_name") or card["department"]).lower()
                    if not any(t.lower() in org for t in target_orgs):
                        return None

                state_raw = card["state_text"]
                region = STATE_REGION_MAP.get(state_raw, "")

                return {
                    "portal_id":       "gem",
                    "bid_number":      card["bid_number"],
                    "org_name":        parsed.get("org_name") or card["department"],
                    "department":      parsed.get("department") or card["department"],
                    "state":           state_raw,
                    "region":          region,
                    "item_category":   parsed.get("item_category") or card["item_category"],
                    "quantity":        parsed.get("quantity", ""),
                    "estimated_value": parsed.get("estimated_value"),
                    "bid_start_date":  parsed.get("bid_start_date", ""),
                    "bid_end_date":    parsed.get("bid_end_date", ""),
                    "keyword_used":    card["keyword_used"],
                    "bid_url":         card["bid_url"],
                }

            with ThreadPoolExecutor(max_workers=PARALLEL_PDF_WORKERS) as pool:
                futures = {pool.submit(process_card, c): c for c in cards}
                done = 0
                for fut in as_completed(futures):
                    done += 1
                    status["pdf_progress"] = int((done / len(cards)) * 100)
                    bid = fut.result()
                    if bid and db.add_bid(bid):
                        total_saved += 1
                        status["bids_found"] = total_saved

        status["log"].append(f"[GeM] Scrape complete. {total_saved} new bids saved.")
    finally:
        try:
            driver.quit()
        except Exception:
            pass

    return total_saved
