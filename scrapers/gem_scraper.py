"""
GeM Portal Scraper — dashboard integration.
Direct port of gem_bid_scraper_fast.py:
  - Same browser setup, same search flow, same card parser, same PDF parser
  - Only changes: print() -> status["log"] and Excel save -> db.add_bid()
"""

import os
import io
import re
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader

# ── Constants (same as gem_bid_scraper_fast.py) ────────────────────────────────

GEM_BASE             = "https://bidplus.gem.gov.in"
AJAX_WAIT            = 7
PAGE_NAV_WAIT        = 5
PDF_TIMEOUT          = 20
PARALLEL_PDF_WORKERS = 10

# Force headless on Railway (no display)
_ON_SERVER = bool(
    os.environ.get("RAILWAY_ENVIRONMENT") or
    os.environ.get("RAILWAY_PROJECT_ID")
)

TARGET_ORGANISATIONS = [
    "BHEL", "Bharat Heavy Electricals", "NTPC", "National Thermal Power",
    "NHPC", "NHAI", "Uttar Pradesh Power Corporation", "PGCIL",
    "Power Grid Corporation", "UPPCL", "PSPCL", "PSTCL", "KPCL", "KPTCL",
    "MSEDCL", "MAHATRANSCO", "MAHAGENCO", "GUVNL", "GETCO",
    "WBSEDCL", "WBSETCL", "JBVNL", "CSPGCL", "CSPDCL",
    "Railways", "Indian Railways", "Power Department", "Energy Department",
    "Electricity Board", "Vidyut", "Transco", "Genco", "DISCOM",
]

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
    "Jharkhand": "East",
    "Madhya Pradesh": "Central", "Chhattisgarh": "Central",
    "Assam": "Northeast",        "Manipur": "Northeast",   "Meghalaya": "Northeast",
    "Mizoram": "Northeast",      "Nagaland": "Northeast",  "Tripura": "Northeast",
    "Arunachal Pradesh": "Northeast", "Sikkim": "Northeast",
}


# ── Browser (same as gem_bid_scraper_fast.py) ──────────────────────────────────

def _make_driver(headless=False):
    o = Options()
    if headless or _ON_SERVER:
        o.add_argument("--headless=new")
    o.add_argument("--no-sandbox")
    o.add_argument("--disable-dev-shm-usage")
    o.add_argument("--disable-gpu")
    o.add_argument("--window-size=1920,1080")
    o.add_argument("--disable-blink-features=AutomationControlled")
    o.add_experimental_option("excludeSwitches", ["enable-automation"])
    o.add_experimental_option("useAutomationExtension", False)
    o.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    drv = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=o)
    drv.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"}
    )
    return drv


# ── Filters (same as gem_bid_scraper_fast.py) ──────────────────────────────────

def _is_target_org(org_text, target_orgs):
    if not target_orgs:
        return True
    if not org_text or org_text == "N/A":
        return False
    org_upper = org_text.upper()
    return any(t.upper() in org_upper for t in target_orgs)


def _is_blocked_category(item_category):
    if not item_category or item_category == "N/A":
        return False
    cat_upper = item_category.upper()
    return any(kw.upper() in cat_upper for kw in BLOCKED_KEYWORDS)


def _card_prefilter(bid, target_orgs):
    if not target_orgs:
        return True
    state = str(bid.get("State / Ministry", "") or "").upper()
    dept  = str(bid.get("Department",       "") or "").upper()
    combined = state + " " + dept
    for t in target_orgs:
        if t.upper() in combined:
            return True
    for kw in CARD_SECTOR_KEYWORDS:
        if kw.upper() in combined:
            return True
    return False


# ── Card parsing (exact copy from gem_bid_scraper_fast.py) ────────────────────

def _parse_bid_cards(soup, keyword):
    results   = []
    container = soup.find("div", id="bidCard")
    if not container:
        return results
    for card in (container.find_all("div", class_="card") or []):
        bid = _parse_single_card(card, keyword)
        if bid:
            results.append(bid)
    return results


def _parse_single_card(card, keyword):
    try:
        bid_link = card.find("a", class_="bid_no_hover")
        if not bid_link:
            return None
        bid_no = bid_link.get_text(strip=True)
        if not re.search(r"GEM/\d{4}/", bid_no, re.I):
            return None

        href = bid_link.get("href", "")
        if href.startswith("/"):
            bid_url = GEM_BASE + href
        elif href.startswith("http"):
            bid_url = href
        else:
            bid_url = GEM_BASE + "/" + href.lstrip("/")

        f = _extract_card_fields(card)
        from datetime import datetime
        return {
            "Bid Number":          bid_no,
            "Organisation Name":   "N/A",
            "Department":          f.get("dept",       "N/A"),
            "State / Ministry":    f.get("state",      "N/A"),
            "Item Category":       "N/A",
            "Quantity":            f.get("quantity",   "N/A"),
            "Estimated Value (Rs)": "N/A",
            "Bid Start Date":      f.get("start_date", "N/A"),
            "Bid End Date":        f.get("end_date",   "N/A"),
            "Keyword Used":        keyword,
            "Bid URL":             bid_url,
            "Scraped On":          datetime.now().strftime("%d-%m-%Y %H:%M"),
        }
    except Exception:
        return None


def _extract_card_fields(card):
    result = {}
    text   = card.get_text(separator=" ", strip=True)

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

    m = re.search(r'Start Date:\s*(\d{2}-\d{2}-\d{4}\s+\d+:\d+\s+(?:AM|PM))', text, re.I)
    if m:
        result["start_date"] = m.group(1).strip()

    m = re.search(r'End Date:\s*(\d{2}-\d{2}-\d{4}\s+\d+:\d+\s+(?:AM|PM))', text, re.I)
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


# ── Pagination (same as gem_bid_scraper_fast.py) ──────────────────────────────

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


# ── Search (same as gem_bid_scraper_fast.py) ──────────────────────────────────

def _search_keyword(driver, keyword, max_pages, status):
    """Mirrors search_keyword() in gem_bid_scraper_fast.py exactly."""
    bids = []
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
            status["log"].append(f"[GeM] '{keyword}': no results")
            return bids

        for page in range(1, max_pages + 1):
            if not status.get("active"):
                break
            soup   = BeautifulSoup(driver.page_source, "lxml")
            parsed = _parse_bid_cards(soup, keyword)
            bids.extend(parsed)
            status["log"].append(f"[GeM] '{keyword}' page {page}: {len(parsed)} bids")
            if page < max_pages:
                if not _go_next_page(driver, page):
                    break
                time.sleep(PAGE_NAV_WAIT)

    except RuntimeError:
        raise
    except Exception as e:
        status["log"].append(f"[GeM] Error on '{keyword}': {e}")

    return bids


# ── PDF (same as gem_bid_scraper_fast.py) ─────────────────────────────────────

def _fetch_pdf_bytes(session, bid_url):
    try:
        r = session.get(bid_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": GEM_BASE,
        }, timeout=PDF_TIMEOUT, stream=True)
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
        return "N/A"

    raw_value = get([
        r"/ Estimated Bid Value\s*\|\s*([\d,\.]+)",
        r"/Estimated Bid Value\s*\|\s*([\d,\.]+)",
        r"Estimated Bid Value\s*\|\s*([\d,\.]+)",
    ])
    est_value = None
    if raw_value and raw_value != "N/A":
        try:
            est_value = float(raw_value.replace(",", ""))
        except ValueError:
            pass

    return {
        "Organisation Name": get([r"/Organisation Name\s*\|\s*([^|]{5,120}?)\s*\|"]),
        "Department":        get([r"/Department Name\s*\|\s*([^|]{5,100}?)\s*\|"]),
        "State / Ministry":  get([r"/Ministry/State Name\s*\|\s*([^|]{3,80}?)\s*\|"]),
        "Item Category":     get([
            r"/Item Category\s*\|\s*(.*?)\s*\|?\s*/Contract Period",
            r"/Item Category\s*\|\s*([^|]{10,300}?)\s*\|",
        ]),
        "Quantity": get([
            r"Total Quantity\s*\|\s*(\d[\d,]*)",
            r"(\d[\d,]*)\s*\|\s*N/A",
        ]),
        "estimated_value": est_value,
        "Bid Start Date": get([
            r"/Bid Start Date/Time\s*\|\s*(\d{2}-\d{2}-\d{4}[^|]{0,20}?)\s*\|",
        ]),
        "Bid End Date": get([
            r"/Bid End Date/Time\s*\|\s*(\d{2}-\d{2}-\d{4}[^|]{0,20}?)\s*\|",
        ]),
    }


def _enrich_one(session, bid):
    """Download + parse PDF for a single bid, then return DB-ready dict."""
    bid_url = bid.get("Bid URL", "")
    if not bid_url or bid_url == "N/A":
        return bid

    pdf_bytes = _fetch_pdf_bytes(session, bid_url)
    if not pdf_bytes:
        return bid

    pdf = _parse_pdf_fields(pdf_bytes)
    DATE_FIELDS = {"Bid Start Date", "Bid End Date"}
    for field, val in pdf.items():
        if field in DATE_FIELDS:
            continue
        if val and val != "N/A":
            bid[field] = val
    return bid


# ── Main entry point ───────────────────────────────────────────────────────────

def run_gem_scrape(keywords, target_orgs, max_pages, status, db, headless=False):
    driver  = _make_driver(headless)
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer":    GEM_BASE,
    })

    all_bids       = []
    total_keywords = len(keywords)

    # ── Phase 1: scrape bid cards for every keyword (mirrors gem_bid_scraper_fast main loop)
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
                bids = _search_keyword(driver, keyword, max_pages, status)
                all_bids.extend(bids)
                if bids:
                    status["log"].append(f"[GeM] '{keyword}': {len(bids)} bids collected")
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

    # ── Phase 2: deduplicate
    seen, unique = set(), []
    for b in all_bids:
        bn = b["Bid Number"]
        if bn not in seen:
            seen.add(bn)
            unique.append(b)
    status["log"].append(f"[GeM] Step 1 — scraped & deduplicated: {len(unique)} bids")

    if not unique:
        status["log"].append("[GeM] No bids found. Done.")
        status["progress"] = 100
        return 0

    # ── Phase 3: card pre-filter
    pre_filtered = [b for b in unique if _card_prefilter(b, target_orgs)]
    dropped = len(unique) - len(pre_filtered)
    status["log"].append(
        f"[GeM] Step 2 — card pre-filter: {len(pre_filtered)} kept / {dropped} dropped"
    )

    # ── Phase 4: skip bids already in DB
    new_candidates = [b for b in pre_filtered if not db.bid_exists("gem", b["Bid Number"])]
    status["log"].append(
        f"[GeM] Step 3 — already in DB: {len(pre_filtered) - len(new_candidates)} skipped | "
        f"{len(new_candidates)} new candidates"
    )

    if not new_candidates:
        status["log"].append("[GeM] Nothing new to add.")
        status["progress"] = 100
        return 0

    # ── Phase 5: parallel PDF enrichment
    status["log"].append(
        f"[GeM] Step 4 — downloading PDFs for {len(new_candidates)} bids "
        f"({PARALLEL_PDF_WORKERS} parallel workers)..."
    )
    status["progress"] = 85

    results = [None] * len(new_candidates)
    done    = [0]
    with ThreadPoolExecutor(max_workers=PARALLEL_PDF_WORKERS) as pool:
        future_to_idx = {
            pool.submit(_enrich_one, session, bid): i
            for i, bid in enumerate(new_candidates)
        }
        for future in as_completed(future_to_idx):
            idx          = future_to_idx[future]
            results[idx] = future.result()
            done[0]     += 1
            status["pdf_progress"] = int(done[0] / len(new_candidates) * 100)

    # ── Phase 6: final org filter + blocked category filter + save to DB
    total_saved = 0
    for bid in results:
        if bid is None:
            continue

        if _is_blocked_category(bid.get("Item Category", "")):
            continue

        if target_orgs and not _is_target_org(bid.get("Organisation Name", ""), target_orgs):
            continue

        state_raw = bid.get("State / Ministry", "")
        region    = STATE_REGION_MAP.get(state_raw, "")

        db_bid = {
            "portal_id":       "gem",
            "bid_number":      bid["Bid Number"],
            "org_name":        bid.get("Organisation Name", ""),
            "department":      bid.get("Department", ""),
            "state":           state_raw,
            "region":          region,
            "item_category":   bid.get("Item Category", ""),
            "quantity":        bid.get("Quantity", ""),
            "estimated_value": bid.get("estimated_value"),
            "bid_start_date":  bid.get("Bid Start Date", ""),
            "bid_end_date":    bid.get("Bid End Date", ""),
            "keyword_used":    bid.get("Keyword Used", ""),
            "bid_url":         bid.get("Bid URL", ""),
        }
        if db.add_bid(db_bid):
            total_saved += 1
            status["bids_found"] = total_saved

    status["log"].append(f"[GeM] Complete. {total_saved} new bids saved to database.")
    status["progress"] = 100
    return total_saved
