from fastapi import APIRouter

from app.api.routes import analytics, ingestion, investors, startups, wonderland

api_router = APIRouter()
api_router.include_router(wonderland.router)
api_router.include_router(analytics.router)
api_router.include_router(ingestion.router)
api_router.include_router(investors.router)
api_router.include_router(startups.router)
