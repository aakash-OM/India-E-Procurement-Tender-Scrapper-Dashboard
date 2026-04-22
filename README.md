# India e-Procurement Tender Scraper Dashboard
### Version 2.0

An interactive 3D web dashboard for monitoring and scraping government tenders across **59 Indian government e-procurement portals** — central, PSU, and all state/UT portals.

---

## Features

### 3D Interactive UI
- Animated Three.js particle network background with mouse parallax
- CSS 3D card tilt effect on every dashboard card (perspective + rotateX/Y)
- Glassmorphism design — blurred glass panels with neon glow accents
- Smooth animated transitions throughout

### Multi-Portal Coverage (59 Portals)
| Category | Portals |
|---|---|
| Central Government | GeM, CPPP, MSTC, NSIC |
| Railways & Defence | IREPS, RITES, IRCON, BEL, HAL, ISRO |
| Power & Energy | NTPC, NHPC, Power Grid, ONGC, GAIL, IOCL, BPCL, HPCL |
| Manufacturing & Infra | BHEL, SAIL, Coal India, NBCC, AAI, NHAI, DMRC |
| State Portals | All 28 states + 6 UTs (UP, MH, GJ, KA, TN, WB, ...) |

> GeM is fully implemented. All other portals are registered and ready for scraper integration.

### Keyword Management
- 85 keywords pre-seeded across 6 categories
- Add new keywords via modal with category selection
- Toggle keywords active/inactive with a single click
- Delete keywords permanently
- Live search filter across all keywords

### Search & Scraping
- Select which portals and keywords to scrape
- Region filter: North / South / East / West / Central / Northeast
- Configurable pages-per-keyword depth
- Headless (background) or visible browser mode
- Real-time scraping log with dual progress bars (overall + PDF processing)
- Smart 6-step pipeline: card pre-filter → deduplication → parallel PDF download → org-name filter → blocked category removal → save

### Results & Analytics
- Filterable results table: by portal, state, keyword
- Export to formatted Excel (.xlsx)
- Pagination
- Live analytics charts:
  - Bids by portal (doughnut)
  - Top 10 states by bid count (horizontal bar)
  - Daily activity timeline (line)
- Stat cards: Total Bids, Today, This Week, Total Value (₹ Cr), Active Keywords

---

## Tech Stack

**Backend**
- Python 3.9+
- Flask 3.0 — web framework and REST API
- SQLite — embedded database (keywords, bids, scrape jobs)
- Selenium 4 + ChromeDriver — browser automation for JS-rendered portals
- BeautifulSoup4 + lxml — HTML parsing
- PyPDF — PDF text extraction
- Requests — HTTP client for PDF downloads
- OpenPyXL — Excel export
- ThreadPoolExecutor — parallel PDF downloads (10 concurrent)

**Frontend**
- Three.js — 3D animated particle network background
- Chart.js — analytics charts (doughnut, bar, line)
- Vanilla JavaScript (ES6+) — SPA logic, API calls, dynamic rendering
- CSS3 — 3D transforms, glassmorphism, custom properties, animations
- Font Awesome 6 — icons
- Google Fonts: Orbitron (headers) + Space Grotesk (body)

---

## Project Structure

```
├── app.py                    # Flask backend — REST API endpoints
├── database.py               # SQLite layer — keywords, bids, jobs
├── portals_config.py         # Registry of all 59 government portals
├── scrapers/
│   └── gem_scraper.py        # GeM portal scraper (Selenium + PDF parsing)
├── templates/
│   └── index.html            # Main dashboard (single-page app)
├── static/
│   ├── css/style.css         # 3D glassmorphism styling
│   └── js/
│       ├── dashboard.js      # Frontend SPA logic
│       └── three-bg.js       # Three.js particle background
├── gem_bid_scraper_fast.py   # Original standalone CLI scraper (v8)
└── requirements_dashboard.txt
```

---

## Setup & Run

```bash
# Install dependencies
pip install -r requirements_dashboard.txt

# Start the dashboard
python app.py
```

Open **http://localhost:5000** in your browser.

---

## Scraping Pipeline (GeM)

```
Search keyword on GeM
        ↓
Collect bid cards (Selenium)
        ↓
Card pre-filter — sector keywords check (State/Dept text)
        ↓
Deduplication — skip already-saved bids
        ↓
Parallel PDF download (10 threads)
        ↓
PDF parsing — extract Org Name, Dept, Value, Dates
        ↓
Organisation filter — keep only target utilities
        ↓
Blocked category filter — remove taxis, repairs, etc.
        ↓
Save to SQLite database
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Dashboard UI |
| GET | `/api/keywords` | List all keywords |
| POST | `/api/keywords` | Add a keyword |
| DELETE | `/api/keywords/<id>` | Delete a keyword |
| POST | `/api/keywords/<id>/toggle` | Toggle active/inactive |
| GET | `/api/portals` | List all 59 portals |
| GET | `/api/bids` | Fetch bids (filterable) |
| GET | `/api/bids/export` | Download Excel file |
| GET | `/api/stats` | Dashboard statistics |
| POST | `/api/search` | Start scraping job |
| GET | `/api/search/status` | Poll scraping progress |
| POST | `/api/search/stop` | Stop active scrape |
| GET | `/api/jobs` | Recent scrape job history |

---

## Target Sector

Primarily configured for **India's power & electrical equipment sector**, tracking bids from:
- State electricity boards and DISCOMs (UPPCL, MSEDCL, GETCO, PSPCL, KPTCL, etc.)
- Central PSUs (NTPC, NHPC, Power Grid, BHEL)
- Railways and heavy industry departments

Keywords cover transformer components, cables, switchgear, substation equipment, metering, SCADA, and more.
