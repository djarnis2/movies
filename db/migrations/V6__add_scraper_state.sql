CREATE TABLE IF NOT EXISTS scraper_state (
    list_id TEXT PRIMARY KEY,
    last_known_page INTEGER NOT NULL DEFAULT 1,
    last_seen_rel_url TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);