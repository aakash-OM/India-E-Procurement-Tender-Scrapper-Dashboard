"""
SQLite database layer for the Gov Tender Dashboard.
"""
import sqlite3
import json
from datetime import datetime, timedelta
from portals_config import DEFAULT_KEYWORDS


class Database:
    def __init__(self, db_path="gov_tenders.db"):
        self.db_path = db_path
        self._init_db()

    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS keywords (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword     TEXT UNIQUE NOT NULL,
                    category    TEXT DEFAULT 'General',
                    is_active   INTEGER DEFAULT 1,
                    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS bids (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    portal_id       TEXT,
                    bid_number      TEXT,
                    org_name        TEXT,
                    department      TEXT,
                    state           TEXT,
                    region          TEXT,
                    item_category   TEXT,
                    quantity        TEXT,
                    estimated_value REAL,
                    bid_start_date  TEXT,
                    bid_end_date    TEXT,
                    keyword_used    TEXT,
                    bid_url         TEXT,
                    scraped_at      TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(portal_id, bid_number)
                );

                CREATE TABLE IF NOT EXISTS scrape_jobs (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    status       TEXT DEFAULT 'pending',
                    portals      TEXT,
                    keywords     TEXT,
                    bids_found   INTEGER DEFAULT 0,
                    started_at   TEXT,
                    completed_at TEXT,
                    error_msg    TEXT
                );
            """)
            self._seed_keywords(conn)

    def _seed_keywords(self, conn):
        existing = conn.execute("SELECT COUNT(*) FROM keywords").fetchone()[0]
        if existing > 0:
            return
        for category, kws in DEFAULT_KEYWORDS.items():
            for kw in kws:
                try:
                    conn.execute(
                        "INSERT OR IGNORE INTO keywords (keyword, category) VALUES (?, ?)",
                        (kw, category)
                    )
                except Exception:
                    pass

    # ── Keywords ──────────────────────────────────────────────────────────────

    def get_keywords(self):
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT id, keyword, category, is_active, created_at FROM keywords ORDER BY category, keyword"
            ).fetchall()
            return [dict(r) for r in rows]

    def add_keyword(self, keyword: str, category: str = "General") -> int:
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT OR IGNORE INTO keywords (keyword, category) VALUES (?, ?)",
                (keyword.strip(), category.strip())
            )
            return cur.lastrowid

    def delete_keyword(self, keyword_id: int):
        with self._conn() as conn:
            conn.execute("DELETE FROM keywords WHERE id = ?", (keyword_id,))

    def toggle_keyword(self, keyword_id: int):
        with self._conn() as conn:
            conn.execute(
                "UPDATE keywords SET is_active = 1 - is_active WHERE id = ?",
                (keyword_id,)
            )

    # ── Bids ──────────────────────────────────────────────────────────────────

    def add_bid(self, bid: dict) -> bool:
        """Returns True if newly inserted, False if duplicate."""
        try:
            with self._conn() as conn:
                conn.execute("""
                    INSERT INTO bids
                      (portal_id, bid_number, org_name, department, state, region,
                       item_category, quantity, estimated_value,
                       bid_start_date, bid_end_date, keyword_used, bid_url, scraped_at)
                    VALUES
                      (:portal_id, :bid_number, :org_name, :department, :state, :region,
                       :item_category, :quantity, :estimated_value,
                       :bid_start_date, :bid_end_date, :keyword_used, :bid_url, :scraped_at)
                """, {
                    "portal_id":       bid.get("portal_id", "gem"),
                    "bid_number":      bid.get("bid_number", ""),
                    "org_name":        bid.get("org_name", ""),
                    "department":      bid.get("department", ""),
                    "state":           bid.get("state", ""),
                    "region":          bid.get("region", ""),
                    "item_category":   bid.get("item_category", ""),
                    "quantity":        bid.get("quantity", ""),
                    "estimated_value": bid.get("estimated_value"),
                    "bid_start_date":  bid.get("bid_start_date", ""),
                    "bid_end_date":    bid.get("bid_end_date", ""),
                    "keyword_used":    bid.get("keyword_used", ""),
                    "bid_url":         bid.get("bid_url", ""),
                    "scraped_at":      datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                })
            return True
        except sqlite3.IntegrityError:
            return False

    def get_bids(self, state=None, region=None, portal=None, keyword=None,
                 date_from=None, date_to=None, min_value=None, max_value=None,
                 limit=100, offset=0):
        where, params = [], []
        if state:
            where.append("state = ?"); params.append(state)
        if region:
            where.append("region = ?"); params.append(region)
        if portal:
            where.append("portal_id = ?"); params.append(portal)
        if keyword:
            where.append("keyword_used LIKE ?"); params.append(f"%{keyword}%")
        if date_from:
            where.append("scraped_at >= ?"); params.append(date_from)
        if date_to:
            where.append("scraped_at <= ?"); params.append(date_to)
        if min_value is not None:
            where.append("estimated_value >= ?"); params.append(min_value)
        if max_value is not None:
            where.append("estimated_value <= ?"); params.append(max_value)

        clause = ("WHERE " + " AND ".join(where)) if where else ""
        params += [limit, offset]
        with self._conn() as conn:
            rows = conn.execute(
                f"SELECT * FROM bids {clause} ORDER BY scraped_at DESC LIMIT ? OFFSET ?",
                params
            ).fetchall()
            total = conn.execute(
                f"SELECT COUNT(*) FROM bids {clause}",
                params[:-2]
            ).fetchone()[0]
        return {"bids": [dict(r) for r in rows], "total": total}

    def bid_exists(self, portal_id: str, bid_number: str) -> bool:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT 1 FROM bids WHERE portal_id=? AND bid_number=?",
                (portal_id, bid_number)
            ).fetchone()
        return row is not None

    # ── Stats ─────────────────────────────────────────────────────────────────

    def get_stats(self):
        today = datetime.now().strftime("%Y-%m-%d")
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        with self._conn() as conn:
            total_bids = conn.execute("SELECT COUNT(*) FROM bids").fetchone()[0]
            today_bids = conn.execute(
                "SELECT COUNT(*) FROM bids WHERE DATE(scraped_at)=?", (today,)
            ).fetchone()[0]
            week_bids = conn.execute(
                "SELECT COUNT(*) FROM bids WHERE DATE(scraped_at)>=?", (week_ago,)
            ).fetchone()[0]
            total_value = conn.execute(
                "SELECT COALESCE(SUM(estimated_value),0) FROM bids"
            ).fetchone()[0]
            total_keywords = conn.execute(
                "SELECT COUNT(*) FROM keywords WHERE is_active=1"
            ).fetchone()[0]

            by_portal = conn.execute("""
                SELECT portal_id, COUNT(*) as count
                FROM bids GROUP BY portal_id ORDER BY count DESC LIMIT 10
            """).fetchall()

            by_state = conn.execute("""
                SELECT state, COUNT(*) as count
                FROM bids WHERE state!='' GROUP BY state ORDER BY count DESC LIMIT 15
            """).fetchall()

            timeline = conn.execute("""
                SELECT DATE(scraped_at) as day, COUNT(*) as count
                FROM bids GROUP BY day ORDER BY day DESC LIMIT 30
            """).fetchall()

            by_category = conn.execute("""
                SELECT keyword_used, COUNT(*) as count
                FROM bids WHERE keyword_used!='' GROUP BY keyword_used ORDER BY count DESC LIMIT 10
            """).fetchall()

        return {
            "total_bids":     total_bids,
            "today_bids":     today_bids,
            "week_bids":      week_bids,
            "total_value":    round(total_value / 1e7, 2),
            "total_keywords": total_keywords,
            "by_portal":      [dict(r) for r in by_portal],
            "by_state":       [dict(r) for r in by_state],
            "timeline":       [dict(r) for r in reversed(timeline)],
            "by_category":    [dict(r) for r in by_category],
        }

    # ── Scrape Jobs ───────────────────────────────────────────────────────────

    def create_job(self, portals: list, keywords: list) -> int:
        with self._conn() as conn:
            cur = conn.execute("""
                INSERT INTO scrape_jobs (portals, keywords, started_at, status)
                VALUES (?, ?, ?, 'running')
            """, (json.dumps(portals), json.dumps(keywords), datetime.now().isoformat()))
            return cur.lastrowid

    def update_job(self, job_id: int, **kwargs):
        fields = ", ".join(f"{k}=?" for k in kwargs)
        values = list(kwargs.values()) + [job_id]
        with self._conn() as conn:
            conn.execute(f"UPDATE scrape_jobs SET {fields} WHERE id=?", values)

    def get_recent_jobs(self, limit=10):
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM scrape_jobs ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]
