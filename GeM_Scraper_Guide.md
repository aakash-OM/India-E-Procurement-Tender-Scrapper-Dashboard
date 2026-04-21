# GeM Portal Bid Scraper — Quick Start Guide

## What This Does
Automatically searches GeM Portal (bidplus.gem.gov.in) for bids matching
your keywords and exports everything to a formatted Excel file — no manual
copy-paste needed.

## Excel Output Columns
| Column               | Description                          |
|----------------------|--------------------------------------|
| Bid Number           | Unique GeM bid ID (e.g. GEM/2024/...) |
| Bid Title            | Name/description of the bid          |
| Department / Buyer   | Government department posting bid    |
| Item Category        | Product/service category             |
| Quantity             | Required quantity                    |
| Estimated Value (₹)  | Estimated contract value             |
| Bid Start Date       | When the bid opened                  |
| Bid End Date         | Deadline to submit                   |
| Keyword Used         | Which keyword matched this bid       |
| Bid URL              | Direct link to the bid on GeM        |
| Scraped On           | Date & time of extraction            |

---

## Step 1 — Install Python
Download from https://python.org (version 3.9 or higher)
Make sure to tick "Add Python to PATH" during installation.

## Step 2 — Install Google Chrome
Download from https://google.com/chrome (if not already installed)

## Step 3 — Install Required Packages
Open Command Prompt (Windows) or Terminal (Mac/Linux) and run:

```
pip install selenium openpyxl webdriver-manager beautifulsoup4
```

## Step 4 — Set Your Keywords
Open `gem_bid_scraper.py` in Notepad or any text editor.
Find this section near the top:

```python
KEYWORDS = [
    "laptop",
    "office furniture",
    "printer",
    # Add your keywords here ↑
]
```

Replace or add your own keywords. Examples:
```python
KEYWORDS = [
    "computer",
    "CCTV camera",
    "solar panel",
    "medical equipment",
    "stationery",
]
```

## Step 5 — Optional Settings
Also in the top of the script, you can change:

```python
MAX_PAGES_PER_KEYWORD = 5   # How many pages to scrape per keyword (10 bids/page)
HEADLESS = True              # False = you can watch the browser open
```

## Step 6 — Run the Script
In Command Prompt/Terminal, navigate to the folder containing the script:

```
cd C:\Users\YourName\Downloads
python gem_bid_scraper.py
```

## Step 7 — Get Your Excel File
The script will create a file named like:
`GeM_Bids_25-03-2026_0930.xlsx`

It contains:
- **Sheet 1 "All Bids"** — All found bids with filters & colour formatting
- **Sheet 2 "Summary"** — Count of bids found per keyword

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError` | Run `pip install selenium openpyxl webdriver-manager beautifulsoup4` |
| `ChromeDriverManager` error | Make sure Google Chrome is installed |
| 0 bids found | GeM may have changed its layout; try `HEADLESS = False` to watch |
| Script runs slowly | Normal — it waits 2 seconds between pages to avoid being blocked |

## Schedule It Daily (Windows)
Use Windows Task Scheduler to run the script every morning automatically:
1. Open Task Scheduler → Create Basic Task
2. Set trigger: Daily at e.g. 8:00 AM
3. Action: Start a program → `python`
4. Arguments: `C:\path\to\gem_bid_scraper.py`

---
*Script targets: https://bidplus.gem.gov.in/all-bids*
*For personal/business use only. Respect GeM portal terms of service.*
