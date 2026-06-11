-- Invest Wonderland schema

CREATE TABLE IF NOT EXISTS ingestion_runs (
    id SERIAL PRIMARY KEY,
    source VARCHAR(32) NOT NULL,
    status VARCHAR(16) NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    records_scraped INTEGER NOT NULL DEFAULT 0,
    records_upserted INTEGER NOT NULL DEFAULT 0,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_ingestion_runs_source_started ON ingestion_runs(source, started_at DESC);

CREATE TABLE IF NOT EXISTS daily_briefings (
    id SERIAL PRIMARY KEY,
    briefing_date DATE NOT NULL UNIQUE,
    lookback_days INTEGER NOT NULL DEFAULT 1,
    payload TEXT NOT NULL,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS investors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(512) NOT NULL,
    investor_type VARCHAR(128),
    check_size_min BIGINT,
    check_size_max BIGINT,
    requirements TEXT,
    website TEXT NOT NULL DEFAULT '',
    logo_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ,
    last_ingestion_run_id INTEGER REFERENCES ingestion_runs(id) ON DELETE SET NULL,
    UNIQUE (name, website)
);

CREATE INDEX IF NOT EXISTS idx_investors_last_seen ON investors(last_seen_at DESC NULLS LAST);

CREATE TABLE IF NOT EXISTS investor_locations (
    id SERIAL PRIMARY KEY,
    investor_id INTEGER NOT NULL REFERENCES investors(id) ON DELETE CASCADE,
    location VARCHAR(256) NOT NULL,
    UNIQUE (investor_id, location)
);

CREATE TABLE IF NOT EXISTS investor_industries (
    id SERIAL PRIMARY KEY,
    investor_id INTEGER NOT NULL REFERENCES investors(id) ON DELETE CASCADE,
    industry VARCHAR(256) NOT NULL,
    UNIQUE (investor_id, industry)
);

CREATE TABLE IF NOT EXISTS investor_stages (
    id SERIAL PRIMARY KEY,
    investor_id INTEGER NOT NULL REFERENCES investors(id) ON DELETE CASCADE,
    stage VARCHAR(128) NOT NULL,
    UNIQUE (investor_id, stage)
);

CREATE TABLE IF NOT EXISTS startups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(512) NOT NULL,
    description TEXT,
    website TEXT NOT NULL DEFAULT '',
    logo_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ,
    last_ingestion_run_id INTEGER REFERENCES ingestion_runs(id) ON DELETE SET NULL,
    UNIQUE (name, website)
);

CREATE INDEX IF NOT EXISTS idx_startups_last_seen ON startups(last_seen_at DESC NULLS LAST);

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
