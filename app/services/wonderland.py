import json
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import DailyBriefing
from app.services.ai_verdict import generate_signal_verdict
from app.services.briefing_fetch import collect_briefing_picks


def build_daily_briefing(session: Session, *, days: int | None = None, refresh: bool = False) -> dict:
    lookback = days if days is not None else settings.feed_lookback_days
    today = date.today()

    if not refresh:
        cached = session.scalar(select(DailyBriefing).where(DailyBriefing.briefing_date == today))
        if cached and cached.lookback_days == lookback:
            return json.loads(cached.payload)

    picks = collect_briefing_picks(session, scrape_live=refresh)
    signals = [{**pick, **generate_signal_verdict(pick)} for pick in picks]

    payload = {
        "date": today.isoformat(),
        "days": lookback,
        "phase": "Validation",
        "version": "1.0",
        "one_liner": settings.app_tagline,
        "signals": signals,
        "ai_enabled": bool(settings.openai_api_key.strip()),
        "sources": ["openvc.app", "startups.gallery"],
        "pick_count": len(signals),
    }

    row = session.scalar(select(DailyBriefing).where(DailyBriefing.briefing_date == today))
    if row:
        row.lookback_days = lookback
        row.payload = json.dumps(payload)
    else:
        session.add(
            DailyBriefing(
                briefing_date=today,
                lookback_days=lookback,
                payload=json.dumps(payload),
            )
        )
    session.commit()
    return payload
