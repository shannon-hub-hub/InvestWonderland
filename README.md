<h1 align="center">VC Intelligence Pipeline</h1>

<p align="center">
A full-stack web application that collects investor and startup data from public directories, normalizes it into a relational database, and surfaces investor focus analytics through a REST API and browser-based interface.
</p>

---

## Overview

This project scrapes two public data sources — [OpenVC](https://www.openvc.app/search) (investor mandates) and [startups.gallery](https://startups.gallery) (startup listings) — and loads the results into a normalized PostgreSQL database. Entities are deduplicated on ingest using a composite unique constraint on `(name, website)`. Each scrape job is recorded as an `IngestionRun` with start time, finish time, record counts, and status, creating an audit trail across runs.

A FastAPI backend exposes the stored data through queryable endpoints: investor search by location, industry, and stage; funding-flow breakdowns by sector, stage, and investor; and a daily briefing that optionally triggers a live scrape. A Next.js frontend provides a unified interface for triggering ingestion, monitoring run status, and browsing analytics.

---

## Built With

- **Python 3.11** — scraping, ETL, and API backend
- **FastAPI** — REST API with automatic OpenAPI documentation
- **SQLAlchemy 2.0** — ORM and query layer
- **PostgreSQL** — primary data store
- **Selenium** — headless browser scraping
- **Next.js / React** — frontend interface
- **Recharts** — analytics charts
- **Docker / Docker Compose** — containerized deployment
- **supercronic** — cron-based scheduled re-ingestion

---

## How It Works

```
Browser → http://localhost:3000  (Next.js)
              ↓  /api/v1/* rewrites
          FastAPI  (:8000)
              ↓
          PostgreSQL
              ↑
          Scheduler  (daily 06:00 UTC)
```

**Data model (simplified)**

```
investors
  ├── investor_locations   (one row per location tag)
  ├── investor_industries  (one row per industry tag)
  └── investor_stages      (one row per stage tag)

startups

ingestion_runs
  (source, status, started_at, finished_at, records_scraped, records_upserted)
```

Investor and startup records carry `created_at` and `updated_at` timestamps. Each upsert updates the parent row in place and reconciles child tag rows, so re-running the scraper reflects changes without duplicating records.

**Analytics endpoints**

| Endpoint | Description |
|---|---|
| `GET /api/v1/analytics/funding-flow` | Sector and stage breakdowns, overview statistics |
| `GET /api/v1/analytics/cooccurrence` | Industry and stage tag pair frequencies |
| `GET /api/v1/investors` | Paginated investor search with location, industry, and stage filters |
| `GET /api/v1/wonderland/briefing` | Daily briefing; add `?refresh=true` to trigger a live scrape |
| `GET /api/v1/ingestion/runs` | Ingestion run history and status |

---

## Installation

**Prerequisites:** Docker and Docker Compose.

```bash
git clone https://github.com/shannon-hub-hub/startup-and-investor-etl-pipeline.git
cd startup-and-investor-etl-pipeline
cp .env.example .env
```

Edit `.env` and set at minimum `DATABASE_URL`. See [Configuration](#configuration) for all options.

```bash
docker compose up -d --build
docker compose run --rm init        # initialize schema and seed data
docker compose up -d scheduler      # optional: start daily cron ingest
open http://localhost:3000
```

**Local development (without Docker for the app)**

```bash
uv pip install -e .
docker compose up -d db             # database only
uv run python scripts/init_db.py
uv run python scripts/seed_data.py
uv run uvicorn app.main:app --reload --port 8000

cd web && npm run dev
open http://localhost:3000
```

API documentation is available at `http://localhost:3000/api/docs` once the server is running.

---

## Running an Ingestion

Trigger a scrape from the Command Center UI, or from the command line:

```bash
# Scrape all sources
uv run python scripts/run_ingestion.py --source all

# Scrape investors only
uv run python scripts/run_ingestion.py --source investors

# Fetch the briefing with a live rescrape
curl -s "http://127.0.0.1:8000/api/v1/wonderland/briefing?refresh=true" | jq '.signals[].name'
```

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | — | PostgreSQL connection string (required) |
| `OPENAI_API_KEY` | — | Optional — enables AI verdicts on briefing picks |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model used for AI verdicts |
| `FEED_LOOKBACK_DAYS` | `30` | Lookback window for briefing analytics |
| `INGEST_MAX_PAGES` | `50` | Maximum pages per investor scrape run |
| `STARTUPS_GALLERY_URL` | — | Override URL for startups.gallery scrape |
| `CORS_ORIGINS` | — | Comma-separated allowed origins for the API |

---

## Limitations

- Deduplication uses exact-match on `(name, website)`. Entities that appear under different names or URLs across sources are not automatically merged.
- The Selenium scrapers depend on the current HTML structure of OpenVC and startups.gallery. Upstream layout changes will require selector updates.
- Funding-flow analytics reflect investor-reported mandate data (sector focus, stage preference, check-size range) scraped from public directories, not verified closed rounds or cap table data.
- On-demand scraping requires a headless browser environment. Hosted deployments without Chrome/Firefox will need the scheduler disabled or replaced with pre-seeded data.

