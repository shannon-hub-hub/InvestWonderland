from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import IngestionRun, Startup
from app.db.session import get_db
from app.schemas.startup import StartupOut
from app.services.ingestion import latest_successful_run

router = APIRouter(prefix="/startups", tags=["startups"])


def _is_stale(entity_last_seen, latest_run: IngestionRun | None) -> bool:
    if latest_run is None or latest_run.finished_at is None:
        return False
    if entity_last_seen is None:
        return True
    return entity_last_seen < latest_run.finished_at


def _to_out(startup: Startup, *, latest_run: IngestionRun | None = None) -> StartupOut:
    return StartupOut(
        id=startup.id,
        name=startup.name,
        description=startup.description,
        website=startup.website,
        logo_url=startup.logo_url,
        created_at=startup.created_at,
        updated_at=startup.updated_at,
        last_seen_at=startup.last_seen_at,
        last_ingestion_run_id=startup.last_ingestion_run_id,
        stale=_is_stale(startup.last_seen_at, latest_run),
    )


@router.get("", response_model=list[StartupOut])
def list_startups(
    q: str | None = Query(None, description="Search by startup name"),
    stale: bool = Query(False, description="Only startups not seen in the latest successful ingest"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    latest_run = latest_successful_run(db, "startups")
    stmt = select(Startup)
    if q:
        stmt = stmt.where(Startup.name.ilike(f"%{q}%"))
    if stale and latest_run and latest_run.finished_at:
        stmt = stmt.where(
            (Startup.last_seen_at.is_(None)) | (Startup.last_seen_at < latest_run.finished_at)
        )
    stmt = stmt.order_by(Startup.name).offset(offset).limit(limit)
    startups = db.scalars(stmt).all()
    return [_to_out(s, latest_run=latest_run) for s in startups]


@router.get("/{startup_id}", response_model=StartupOut)
def get_startup(startup_id: int, db: Session = Depends(get_db)):
    startup = db.get(Startup, startup_id)
    if startup is None:
        raise HTTPException(status_code=404, detail="Startup not found")
    return _to_out(startup, latest_run=latest_successful_run(db, "startups"))
