"""Live briefing picks from OpenVC + startups.gallery scrapers."""

from __future__ import annotations

import logging
import re
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.config import settings
from app.db.models import Investor, Startup
from app.services.ingest_source import ingest_investors_if_idle, ingest_startups_if_idle

logger = logging.getLogger(__name__)

OPENVC_SOURCE = "openvc.app"
GALLERY_SOURCE = "startups.gallery"


def _slug(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "pick"


def _format_check(min_val: str | None, max_val: str | None) -> str:
    parts = [p for p in (min_val, max_val) if p]
    if not parts:
        return "Check size n/a"
    if len(parts) == 2 and parts[0] != parts[1]:
        return f"${parts[0]}–${parts[1]}"
    return f"${parts[0]}"


def _first_industry(raw: str | None) -> str:
    if not raw:
        return "General"
    return raw.split(",")[0].strip() or "General"


def openvc_record_to_pick(record: dict[str, Any], rank: int) -> dict[str, Any]:
    name = record["name"]
    return {
        "rank": rank,
        "name": name,
        "slug": f"openvc-{_slug(name)}",
        "tagline": (record.get("type") or "Investor").strip(),
        "summary": (record.get("requirements") or record.get("industries") or "").strip(),
        "sector": _first_industry(record.get("industries")),
        "stage": (record.get("stage") or "—").strip(),
        "amount_usd": 0,
        "estimated_raise": _format_check(record.get("check_min"), record.get("check_max")),
        "announced_at": date.today().isoformat(),
        "website": (record.get("website") or "").strip(),
        "logo_url": record.get("logo_url"),
        "source_url": "https://www.openvc.app/search",
        "source": OPENVC_SOURCE,
        "pick_kind": "investor",
        "locations": (record.get("locations") or "").strip(),
        "investors": [],
    }


def gallery_record_to_pick(record: dict[str, Any], rank: int) -> dict[str, Any]:
    name = record["name"]
    description = (record.get("description") or "").strip()
    return {
        "rank": rank,
        "name": name,
        "slug": f"gallery-{_slug(name)}",
        "tagline": description[:120] if description else "Startup on startups.gallery",
        "summary": description,
        "sector": "Startup",
        "stage": "Series C+",
        "amount_usd": 0,
        "estimated_raise": "—",
        "announced_at": date.today().isoformat(),
        "website": (record.get("website") or "").strip(),
        "logo_url": record.get("logo_url"),
        "source_url": settings.startups_gallery_url,
        "source": GALLERY_SOURCE,
        "pick_kind": "company",
        "locations": "",
        "investors": [],
    }


def _db_openvc_fallback(session: Session) -> list[dict]:
    stmt = (
        select(Investor)
        .options(
            selectinload(Investor.locations),
            selectinload(Investor.industries),
            selectinload(Investor.stages),
        )
        .order_by(Investor.last_seen_at.desc().nulls_last(), Investor.updated_at.desc())
    )
    rows = session.scalars(stmt).all()
    records = []
    for inv in rows:
        records.append(
            {
                "name": inv.name,
                "type": inv.investor_type or "Investor",
                "locations": ", ".join(row.location for row in inv.locations),
                "check_min": str(inv.check_size_min or ""),
                "check_max": str(inv.check_size_max or ""),
                "stage": ", ".join(row.stage for row in inv.stages),
                "requirements": inv.requirements or "",
                "industries": ", ".join(row.industry for row in inv.industries),
                "website": inv.website or "",
                "logo_url": inv.logo_url,
            }
        )
    return records


def _db_gallery_fallback(session: Session) -> list[dict]:
    stmt = select(Startup).order_by(Startup.last_seen_at.desc().nulls_last(), Startup.updated_at.desc())
    rows = session.scalars(stmt).all()
    return [
        {
            "name": s.name,
            "description": s.description or "",
            "website": s.website or "",
            "logo_url": s.logo_url,
        }
        for s in rows
    ]


def _live_openvc_records(session: Session) -> list[dict]:
    try:
        data = ingest_investors_if_idle(session)
        if data is not None:
            return data
        logger.info("Investor ingest already running; briefing uses DB fallback for OpenVC")
    except Exception:
        logger.exception("Briefing investor ingest failed; using DB fallback")
    return _db_openvc_fallback(session)


def _live_gallery_records(session: Session) -> list[dict]:
    try:
        data = ingest_startups_if_idle(session)
        if data is not None:
            return data
        logger.info("Startup ingest already running; briefing uses DB fallback for gallery")
    except Exception:
        logger.exception("Briefing startup ingest failed; using DB fallback")
    return _db_gallery_fallback(session)


def collect_briefing_picks(session: Session, *, scrape_live: bool = True) -> list[dict]:
    """Return all OpenVC investors and gallery companies (live ingest or DB fallback)."""
    if scrape_live:
        openvc_raw = _live_openvc_records(session)
        gallery_raw = _live_gallery_records(session)
    else:
        openvc_raw = _db_openvc_fallback(session)
        gallery_raw = _db_gallery_fallback(session)

    picks: list[dict] = []
    rank = 1
    for record in openvc_raw:
        picks.append(openvc_record_to_pick(record, rank))
        rank += 1
    for record in gallery_raw:
        picks.append(gallery_record_to_pick(record, rank))
        rank += 1

    return picks
