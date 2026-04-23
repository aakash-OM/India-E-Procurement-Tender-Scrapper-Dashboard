"""
GeM Portal Scraper – dashboard integration layer.
Logic ported from gem_bid_scraper_fast.py (v8).
Progress is reported via the shared `status` dict instead of console prints.
"""

import os
import time
import re
import io
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# On Railway (or any server without a display), headless is always forced.
_ON_RAILWAY = bool(os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("RAILWAY_PROJECT_ID"))

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

GEM_BASE             = "https://bidplus.gem.gov.in"
AJAX_WAIT            = 7
PAGE_NAV_WAIT        = 5
PDF_TIMEOUT          = 20
PARALLEL_PDF_WORKERS = 10

CARD_SECTOR_KEYWORDS = [
    "Power", "Energy", "Electric", "Vidyut", "Bijli",
    "Transco", "Genco", "Discom", "Grid",
    "Transmission", "Generation", "Distribution",
    "Railways", "Railway", "NTPC", "BHEL", "NHPC", "PGCIL", "NHAI",
    "Heavy Industries",
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
    "Paint", "Zinc", "Resin", "Acid",
]

STATE_REGION_MAP = {
    "Uttar Pradesh": "North",    "Haryana": "North",      "Punjab": "North",
    "Rajasthan": "North",        "Delhi": "North",         "Himachal Pradesh": "North",
    "Uttarakhand": "North",      "Jammu & Kashmir": "North",
    "Maharashtra": "West",       "Gujarat": "West",        "Goa": "West",
    "Karnataka": "South",        "Telangana": "South",     "Andhra Pradesh": "South",
    "Tamil Nadu": "South",       "Kerala": "South",
    "West Bengal": "East",       "Odisha": "East",         "Bihar": "East",
    "Jharkhand": "East",         "Madhya Pradesh": "Central", "Chhattisgarh": "Central",
    "Assam": "Northeast",        "Manipur": "Northeast",   "Meghalaya": "Northeast",
    "Mizoram": "Northeast",      "Nagaland": "Northeast",  "Tripura": "Northeast",
    "Arunachal Pradesh": "Northeast", "Sikkim": "Northeast",
}


# ── Browser ────────────────────────────────────────────────────────────────────

def _make_driver(headless=True):
    opts = Options()
    if headless or _ON_RAILWAY:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    svc = ChromeService(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=svc, options=opts)
    drv.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"}
    )
    return drv


# ── Card field extraction from plain text ──────────────────────────────────────

def _extract_card_fields_from_text(text):
    """Parse dept/state/dates from a bid card's plain text (works on both
    Selenium .text and BeautifulSoup get_text output)."""
    result = {}

    m = re.match(r'^([\d,\.]+)\s+Department Name And Address:', text, re.I)
    if m:
        result["quantity"] = m.group(1).replace(",", "").strip()

    m = re.search(r'Department Name And Address:\s*(.+?)\s+Start Date:', text, re.I | re.S)
    if m:
        dept_block = re.sub(r'\s*\bNA\b\s*$', '', m.group(1).strip()).strip()
        ministry, dept = _split_ministry_dept(dept_block)
        result["state"] = ministry
        if dept:
            result["dept"] = dept

    m = re.search(r'Start Date:\s*(\d{2}-\d{2}-\d{4}[^E]{0,25}?)(?:\s+End|\s*$)', text, re.I)
    if m:
        result["start_date"] = m.group(1).strip()

    m = re.search(r'End Date:\s*(\d{2}-\d{2}-\d{4}(?:\s+\d+:\d+\s+(?:AM|PM))?)', text, re.I)
    if m:
        result["end_date"] = m.group(1).strip()

    return result


def _split_ministry_dept(dept_block):
    if dept_block.startswith("PMO "):
        return ("PMO", dept_block[4:].strip())
    m = re.match(
        r'^(Ministry of [^,]+?)\s+'
        r'((?:Department|Directorate|Office|Authority|Board|Commission|'
        r'Council|Secretariat|Division).+)$', dept_block, re.I)
    if m:
        return (m.group(1).strip(), m.group(2).strip())
    m = re.match(
        r'^(Ministry of [^,]+?)\s+([A-Z]{2}[A-Z\s]+(?:Limited|Ltd|Corporation|Board).*)$',
        dept_block)
    if m:
        return (m.group(1).strip(), m.group(2).strip())
    m = re.match(
        r'^(Ministry of \w+(?:\s+\w+)?)\s+((?:Indian|Central|National|State)\s+\w.+)$',
        dept_block, re.I)
    if m:
        return (m.group(1).strip(), m.group(2).strip())
    return (dept_block, None)


def _build_card(bid_no, bid_url, card_text, keyword):
    f = _extract_card_fields_from_text(card_text)
    return {
        "bid_number":    bid_no,
        "bid_url":       bid_url,
        "department":    f.get("dept",       ""),
        "state_text":    f.get("state",      ""),
        "item_category": "",
        "quantity":      f.get("quantity",   ""),
        "keyword_used":  keyword,
        "start_date":    f.get("start_date", ""),
        "end_date":      f.get("end_date",   ""),
    }


def _make_bid_url(href):
    if href.startswith("http"):
        return href
    return GEM_BASE + ("/" if not href.startswith("/") else "") + href.lstrip("/")


# ── Card extraction – Selenium (primary) ──────────────────────────────────────

def _extract_cards_selenium(driver, keyword, status):
    """
    Uses the live Selenium DOM to pull bid cards.
    More reliable than BeautifulSoup on page_source because we already know
    a.bid_no_hover elements exist (WebDriverWait confirmed it).
    """
    cards = []
    bid_links = driver.find_elements(By.CSS_SELECTOR, "a.bid_no_hover")
    status["log"].append(f"[GeM] Selenium DOM: {len(bid_links)} bid links found")

    for link in bid_links:
        try:
            bid_no = link.text.strip()
            if not re.search(r"GEM/\d{4}/", bid_no, re.I):
                continue
            bid_url = _make_bid_url(link.get_attribute("href") or "")

            # Try to get the enclosing card's text (walks up to div.card or similar)
            card_text = ""
            try:
                ancestor = link.find_element(
                    By.XPATH,
                    "ancestor::div[contains(@class,'card') or contains(@class,'bid_no')][1]"
                )
                card_text = ancestor.text
            except Exception:
                try:
                    card_text = link.find_element(By.XPATH, "../..").text
                except Exception:
                    card_text = bid_no

            cards.append(_build_card(bid_no, bid_url, card_text, keyword))
        except Exception:
            continue
    return cards


# ── Card extraction – BeautifulSoup (fallback) ────────────────────────────────

def _extract_cards_bs4(driver, keyword, status):
    """
    Fallback: parse driver.page_source with BeautifulSoup.
    Searches the whole page for a.bid_no_hover so it works even if the
    container div id/class has changed.
    """
    cards = []
    soup = BeautifulSoup(driver.page_source, "lxml")
    bid_links = soup.find_all("a", class_="bid_no_hover")
    status["log"].append(f"[GeM] BS4 fallback: {len(bid_links)} bid links found")

    for link in bid_links:
        try:
            bid_no = link.get_text(strip=True)
            if not re.search(r"GEM/\d{4}/", bid_no, re.I):
                continue
            bid_url = _make_bid_url(link.get("href", ""))

            card_el = (
                link.find_parent("div", class_="card") or
                link.find_parent("div", class_=lambda c: c and "bid" in c.lower()) or
                link.parent
            )
            card_text = card_el.get_text(separator=" ", strip=True) if card_el else bid_no
            cards.append(_build_card(bid_no, bid_url, card_text, keyword))
        except Exception:
            continue
    return cards


# ── Pagination ─────────────────────────────────────────────────────────────────

def _go_next_page(driver, current_page):
    try:
        links  = driver.find_elements(By.CSS_SELECTOR, "#light-pagination a, .pagination2 a")
        target = str(current_page + 1)
        for lnk in links:
            if lnk.text.strip() == target:
                lnk.click()
                return True
        for lnk in links:
            if "»" in lnk.text or lnk.get_attribute("rel") == "next":
                lnk.click()
                return True
    except Exception:
        pass
    return False


# ── Per-keyword search ─────────────────────────────────────────────────────────

def _search_keyword(driver, keyword, max_pages, status):
    cards = []
    status["log"].append(f"[GeM] Searching: '{keyword}'")

    try:
        _ = driver.title
    except Exception:
        raise RuntimeError("browser_dead")

    try:
        driver.get(f"{GEM_BASE}/all-bids")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "searchBid"))
        )
        time.sleep(2)

        box = driver.find_element(By.ID, "searchBid")
        box.clear()
        box.send_keys(keyword)
        time.sleep(0.5)
        driver.find_element(By.ID, "searchBidRA").click()
        time.sleep(AJAX_WAIT)

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.bid_no_hover"))
            )
        except Exception:
            status["log"].append(f"[GeM] '{keyword}': no results found on GeM")
            return cards

        for page in range(1, max_pages + 1):
            if not status.get("active"):
                break

            # Primary: use Selenium live DOM
            page_cards = _extract_cards_selenium(driver, keyword, status)

            # Fallback: parse page_source with BeautifulSoup
            if not page_cards:
                page_cards = _extract_cards_bs4(driver, keyword, status)

            cards.extend(page_cards)
            status["log"].append(f"[GeM] '{keyword}' page {page}: {len(page_cards)} cards extracted")

            if page < max_pages:
                if not _go_next_page(driver, page):
                    break
                time.sleep(PAGE_NAV_WAIT)

    except RuntimeError:
        raise
    except Exception as e:
        status["log"].append(f"[GeM] Error on '{keyword}': {e}")

    return cards


# ── PDF fetching & parsing ─────────────────────────────────────────────────────

def _fetch_pdf_bytes(session, bid_url):
    try:
        r = session.get(bid_url, timeout=PDF_TIMEOUT, stream=True)
        if r.status_code == 200 and "pdf" in r.headers.get("content-type", "").lower():
            return r.content
    except Exception:
        pass
    return None


def _parse_pdf_fields(pdf_bytes):
    if not pdf_bytes:
        return {}
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
    except Exception:
        return {}

    raw_text = ""
    for page in reader.pages:
        try:
            raw_text += (page.extract_text() or "") + "\n"
        except Exception:
            continue

    if not raw_text.strip():
        return {}

    clean_lines = []
    for line in raw_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if sum(1 for c in line if ord(c) < 128) / len(line) > 0.5:
            clean_lines.append(line)
    text = " | ".join(clean_lines)
    if not text:
        return {}

    def get(patterns):
        for pat in patterns:
            try:
                m = re.search(pat, text, re.IGNORECASE | re.S)
                if m:
                    val = m.group(1).strip().strip("|").strip()
                    val = re.sub(r'\b(\w+)\s+\1\b', r'\1', val)
                    val = re.sub(r'\s*\|\s*', ' ', val).strip()
                    if val and 2 < len(val) < 400:
                        return val
            except Exception:
                continue
        return ""

    raw_value = get([
        r"/ Estimated Bid Value\s*\|\s*([\d,\.]+)",
        r"/Estimated Bid Value\s*\|\s*([\d,\.]+)",
        r"Estimated Bid Value\s*\|\s*([\d,\.]+)",
    ])
    est_value = None
    if raw_value:
        try:
            est_value = float(raw_value.replace(",", ""))
        except ValueError:
            pass

    return {
        "org_name":       get([r"/Organisation Name\s*\|\s*([^|]{5,120}?)\s*\|"]),
        "department":     get([r"/Department Name\s*\|\s*([^|]{5,100}?)\s*\|"]),
        "state":          get([r"/Ministry/State Name\s*\|\s*([^|]{3,80}?)\s*\|"]),
        "item_category":  get([
            r"/Item Category\s*\|\s*(.*?)\s*\|?\s*/Contract Period",
            r"/Item Category\s*\|\s*([^|]{10,300}?)\s*\|",
        ]),
        "quantity":       get([
            r"Total Quantity\s*\|\s*(\d[\d,]*)",
            r"(\d[\d,]*)\s*\|\s*N/A",
        ]),
        "estimated_value": est_value,
        "bid_start_date": get([r"/Bid Start Date/Time\s*\|\s*(\d{2}-\d{2}-\d{4}[^|]{0,20}?)\s*\|"]),
        "bid_end_date":   get([r"/Bid End Date/Time\s*\|\s*(\d{2}-\d{2}-\d{4}[^|]{0,20}?)\s*\|"]),
    }


# ── Per-bid PDF enrichment ─────────────────────────────────────────────────────

def _enrich_one(session, card):
    pdf_bytes = _fetch_pdf_bytes(session, card["bid_url"])
    parsed    = _parse_pdf_fields(pdf_bytes)

    item_cat = parsed.get("item_category") or card.get("item_category", "")
    if item_cat and any(b.upper() in item_cat.upper() for b in BLOCKED_KEYWORDS):
        return None

    state_raw = parsed.get("state") or card.get("state_text", "")
    region    = STATE_REGION_MAP.get(state_raw, "")

    return {
        "portal_id":       "gem",
        "bid_number":      card["bid_number"],
        "org_name":        parsed.get("org_name") or card.get("department", ""),
        "department":      parsed.get("department") or card.get("department", ""),
        "state":           state_raw,
        "region":          region,
        "item_category":   item_cat,
        "quantity":        parsed.get("quantity") or card.get("quantity", ""),
        "estimated_value": parsed.get("estimated_value"),
        "bid_start_date":  parsed.get("bid_start_date") or card.get("start_date", ""),
        "bid_end_date":    parsed.get("bid_end_date") or card.get("end_date", ""),
        "keyword_used":    card["keyword_used"],
        "bid_url":         card["bid_url"],
    }


# ── Card pre-filter ────────────────────────────────────────────────────────────

def _card_prefilter(card, target_orgs):
    if not target_orgs:
        return True
    state = (card.get("state_text") or "").upper()
    dept  = (card.get("department") or "").upper()
    combined = state + " " + dept
    for t in target_orgs:
        if t.upper() in combined:
            return True
    for kw in CARD_SECTOR_KEYWORDS:
        if kw.upper() in combined:
            return True
    return False


# ── Main entry point ───────────────────────────────────────────────────────────

def run_gem_scrape(keywords, target_orgs, max_pages, status, db, headless=True):
    driver  = _make_driver(headless)
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer":    GEM_BASE,
    })

    total_saved    = 0
    total_keywords = len(keywords)
    all_cards      = []

    # Phase 1: browse GeM and collect bid cards for every keyword
    try:
        kw_idx = 0
        while kw_idx < total_keywords:
            if not status.get("active"):
                break
            keyword = keywords[kw_idx]
            status.update({
                "current_portal":  "GeM",
                "current_keyword": keyword,
                "progress":        int((kw_idx / total_keywords) * 80),
            })
            try:
                cards = _search_keyword(driver, keyword, max_pages, status)
                all_cards.extend(cards)
                kw_idx += 1
                time.sleep(1)
            except RuntimeError:
                status["log"].append("[GeM] Browser crashed — restarting...")
                try:
                    driver.quit()
                except Exception:
                    pass
                driver = _make_driver(headless)
    finally:
        try:
            driver.quit()
        except Exception:
            pass

    # Phase 2: deduplicate within this run
    seen, unique = set(), []
    for c in all_cards:
        bn = c["bid_number"]
        if bn not in seen:
            seen.add(bn)
            unique.append(c)
    status["log"].append(f"[GeM] {len(unique)} unique bid cards scraped across all keywords")

    # Phase 3: card pre-filter + DB duplicate check
    candidates = []
    for c in unique:
        if not _card_prefilter(c, target_orgs):
            continue
        if db.bid_exists("gem", c["bid_number"]):
            continue
        candidates.append(c)
    status["log"].append(f"[GeM] {len(candidates)} new candidates after pre-filter")

    if not candidates:
        status["log"].append("[GeM] Nothing new to add.")
        status["progress"] = 100
        return 0

    # Phase 4: parallel PDF enrichment + save
    status["log"].append(
        f"[GeM] Downloading PDFs for {len(candidates)} bids ({PARALLEL_PDF_WORKERS} parallel workers)..."
    )
    status["progress"] = 85

    done_count = 0
    with ThreadPoolExecutor(max_workers=PARALLEL_PDF_WORKERS) as pool:
        futures = {pool.submit(_enrich_one, session, c): c for c in candidates}
        for fut in as_completed(futures):
            done_count += 1
            status["pdf_progress"] = int((done_count / len(candidates)) * 100)
            bid = fut.result()
            if bid is None:
                continue
            if target_orgs:
                org = (bid.get("org_name") or "").upper()
                if not any(t.upper() in org for t in target_orgs):
                    continue
            if db.add_bid(bid):
                total_saved += 1
                status["bids_found"] = total_saved

    status["log"].append(f"[GeM] Complete. {total_saved} new bids saved.")
    status["progress"] = 100
    return total_saved
