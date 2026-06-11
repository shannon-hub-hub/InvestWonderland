# Invest Wonderland

Retro desktop web app with a **Command Center**: scrape OpenVC & startups.gallery, funding-flow analytics, and data tables in one Next.js UI.

**Palette:** `#503D2D` · `#1F9295` · `#F0ECC9` · `#E3AD43` · `#D44C1A`

## Architecture

```
Browser → http://localhost:3000  (Next.js)
              ↓ rewrites /api/v1/*
          FastAPI (:8000)
              ↓
          PostgreSQL
```

| Surface | URL |
|---------|-----|
| **Web app** | http://localhost:3000 |
| **Command Center** | http://localhost:3000 |
| **API docs** | http://localhost:3000/api/docs |
| **Analytics** | `GET /api/v1/analytics/funding-flow` |
| **Briefing API** | `GET /api/v1/wonderland/briefing` |

## Quick start

```bash
cd /Users/shannonchiang/projects/scraper
cp .env.example .env
docker compose up -d --build
docker compose run --rm init
docker compose up -d scheduler   # daily ingest cron
open http://localhost:3000
```

### Local dev

```bash
uv pip install -e .
docker compose up -d db
uv run python scripts/init_db.py
uv run uvicorn app.main:app --reload --port 8000

cd web && npm run dev
open http://localhost:3000
```

## Data

- **Briefing API** — OpenVC investors + startups.gallery companies (`GET /api/v1/wonderland/briefing?refresh=true`).
- **Investors / startups** — optional Selenium scrapers (`investors`, `startups` ingest sources).
- **Crunchbase proxy** — optional, not used by the briefing.

```bash
uv run python scripts/run_ingestion.py --source seed
curl -s "http://127.0.0.1:8000/api/v1/wonderland/briefing?refresh=true" | jq '.signals[].name'
```

## Configuration

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Optional — AI verdicts on briefing picks |
| `CRUNCHBASE_API_KEY` | Optional — `/api/v1/proxy/crunchbase/*` only |
| `FEED_LOOKBACK_DAYS` | Briefing cache metadata (default `30`) |
| `FEED_PICK_COUNT` | Total picks per briefing (default `10`) |
| `BRIEFING_PER_SOURCE` | Picks per site (default `5`) |
| `STARTUPS_GALLERY_URL` | Gallery scrape URL for briefing |

## Troubleshooting (Next.js dev)

If you see `Cannot find module './682.js'` (or similar):

```bash
lsof -ti :3000 | xargs kill -9
cd web && npm run dev
```

`npm run dev` now clears `.next` automatically. Avoid running `npm run build` and `npm run dev` back-to-back without a clean.
