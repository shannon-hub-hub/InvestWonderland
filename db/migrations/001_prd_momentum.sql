-- Daily briefing cache
CREATE TABLE IF NOT EXISTS daily_briefings (
    id SERIAL PRIMARY KEY,
    briefing_date DATE NOT NULL UNIQUE,
    lookback_days INTEGER NOT NULL DEFAULT 1,
    payload TEXT NOT NULL,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
