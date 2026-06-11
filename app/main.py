from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.v1.router import api_router
from app.config import settings
from app.db.session import engine


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Invest Wonderland — daily funding briefing + investor/startup scraper data.",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "database": "connected",
        "api": settings.api_version,
        "features": {
            "investors": True,
            "startups": True,
            "analytics": True,
            "ingestion_stats": True,
            "wonderland_briefing": True,
        },
    }


@app.get("/")
def root():
    return {
        "service": settings.api_title,
        "web_app": "http://localhost:3000",
        "docs": "/api/docs",
        "api": "/api/v1",
        "briefing": "/api/v1/wonderland/briefing",
        "ingestion": "POST /api/v1/ingestion/runs",
        "snapshots": "/api/v1/ingestion/runs/{run_id}/snapshots/investors",
        "funding_flow": "/api/v1/analytics/funding-flow",
        "cooccurrence": "/api/v1/analytics/cooccurrence",
        "scheduler": "docker compose up -d scheduler (daily 06:00 UTC)",
    }
