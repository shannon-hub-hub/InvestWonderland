-- Longitudinal snapshots: full entity state per ingestion run

CREATE TABLE IF NOT EXISTS investor_snapshots (
    id SERIAL PRIMARY KEY,
    ingestion_run_id INTEGER NOT NULL REFERENCES ingestion_runs(id) ON DELETE CASCADE,
    investor_id INTEGER REFERENCES investors(id) ON DELETE SET NULL,
    name VARCHAR(512) NOT NULL,
    website TEXT NOT NULL DEFAULT '',
    investor_type VARCHAR(128),
    check_size_min BIGINT,
    check_size_max BIGINT,
    requirements TEXT,
    logo_url TEXT,
    locations JSONB NOT NULL DEFAULT '[]',
    industries JSONB NOT NULL DEFAULT '[]',
    stages JSONB NOT NULL DEFAULT '[]',
    snapshotted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_investor_snapshots_run ON investor_snapshots(ingestion_run_id);
CREATE INDEX IF NOT EXISTS idx_investor_snapshots_investor ON investor_snapshots(investor_id);
CREATE INDEX IF NOT EXISTS idx_investor_snapshots_at ON investor_snapshots(snapshotted_at DESC);

CREATE TABLE IF NOT EXISTS startup_snapshots (
    id SERIAL PRIMARY KEY,
    ingestion_run_id INTEGER NOT NULL REFERENCES ingestion_runs(id) ON DELETE CASCADE,
    startup_id INTEGER REFERENCES startups(id) ON DELETE SET NULL,
    name VARCHAR(512) NOT NULL,
    website TEXT NOT NULL DEFAULT '',
    description TEXT,
    logo_url TEXT,
    snapshotted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_startup_snapshots_run ON startup_snapshots(ingestion_run_id);
CREATE INDEX IF NOT EXISTS idx_startup_snapshots_startup ON startup_snapshots(startup_id);
CREATE INDEX IF NOT EXISTS idx_startup_snapshots_at ON startup_snapshots(snapshotted_at DESC);
