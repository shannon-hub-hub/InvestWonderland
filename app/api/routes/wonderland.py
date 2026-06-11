from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.wonderland import WonderlandBriefing
from app.services.wonderland import build_daily_briefing

router = APIRouter(prefix="/wonderland", tags=["wonderland"])


@router.get("/briefing", response_model=WonderlandBriefing)
def get_daily_briefing(
    days: int | None = Query(None, ge=1, le=7),
    refresh: bool = Query(False, description="Bypass cached briefing for today"),
    db: Session = Depends(get_db),
):
    """Daily briefing: all scraped OpenVC investors + gallery companies with AI verdict."""
    return build_daily_briefing(db, days=days, refresh=refresh)
