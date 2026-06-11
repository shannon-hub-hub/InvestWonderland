-- Track when each entity was last observed in a scrape batch

ALTER TABLE investors ADD COLUMN IF NOT EXISTS last_seen_at TIMESTAMPTZ;
ALTER TABLE investors ADD COLUMN IF NOT EXISTS last_ingestion_run_id INTEGER REFERENCES ingestion_runs(id) ON DELETE SET NULL;

ALTER TABLE startups ADD COLUMN IF NOT EXISTS last_seen_at TIMESTAMPTZ;
ALTER TABLE startups ADD COLUMN IF NOT EXISTS last_ingestion_run_id INTEGER REFERENCES ingestion_runs(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_investors_last_seen ON investors(last_seen_at DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_startups_last_seen ON startups(last_seen_at DESC NULLS LAST);
