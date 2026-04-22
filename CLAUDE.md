# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Dashboard

```bash
python app.py
# Opens at http://localhost:5000
```

The original standalone CLI scraper (no Flask) can still be run independently:
```bash
python gem_bid_scraper_fast.py
```

## Installing Dependencies

```bash
pip install -r requirements_dashboard.txt
```

## Architecture

This is a **Flask + SQLite + Selenium** web dashboard with a vanilla JS single-page frontend.

### Request Flow

```
Browser (index.html) → fetch /api/* → app.py → database.py (SQLite)
                                              ↘ scrapers/gem_scraper.py (Selenium)
```

Scraping runs in a **background `threading.Thread`**. The frontend polls `/api/search/status` every 2.5 seconds to get live progress. There is no WebSocket — status is shared via the module-level `scrape_status` dict in `app.py`.

### Key Files and Their Roles

- **`app.py`** — All Flask routes. Holds the `scrape_status` dict (single-worker model; only one scrape job can run at a time). Spawns the background thread on `POST /api/search`.
- **`database.py`** — All SQLite access via a `Database` class. Three tables: `keywords`, `bids`, `scrape_jobs`. Keywords are seeded from `portals_config.DEFAULT_KEYWORDS` on first run only.
- **`portals_config.py`** — Single source of truth for all 59 portal definitions and the `DEFAULT_KEYWORDS` dict (6 categories, 85 keywords). Any new portal must be added here and appended to `ALL_PORTALS`.
- **`scrapers/gem_scraper.py`** — The only implemented scraper. Entry point is `run_gem_scrape(keywords, target_orgs, max_pages, status, db, headless)`. It mutates the `status` dict directly for live progress reporting. Uses `ThreadPoolExecutor` (10 workers) for parallel PDF downloads.
- **`templates/index.html`** — Single HTML file; loads Three.js and Chart.js from CDN. All sections (Dashboard, Portals, Keywords, Search, Results) exist in the DOM simultaneously — `dashboard.js` toggles `.active` to show/hide.
- **`static/js/dashboard.js`** — All frontend state lives in the `state` object. `loadPortals()` must complete before `renderSearchPortalChips()` works (portals data dependency).

### Adding a New Portal Scraper

1. Add the portal entry to the appropriate list in `portals_config.py` with `"implemented": True`.
2. Create `scrapers/<portal_id>_scraper.py` with a `run_<portal_id>_scrape(keywords, target_orgs, max_pages, status, db)` function matching the same signature as `run_gem_scrape`.
3. Import and call it inside the `worker()` function in `app.py` under the `for portal_id in portals` loop.

### Database

SQLite file is `gov_tenders.db` (created automatically on first run). Bids have a `UNIQUE(portal_id, bid_number)` constraint — `db.add_bid()` returns `True` on insert, `False` on duplicate.

### Windows-Specific Notes

- All `print()` calls must use ASCII characters only — the Windows console (cp1252) cannot encode Unicode arrows or symbols.
- The `venv/` directory and `gov_tenders.db` should be in `.gitignore` but currently are not — avoid committing them.
