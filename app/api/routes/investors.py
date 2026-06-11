from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import IngestionRun, Investor
from app.db.session import get_db
from app.schemas.investor import InvestorOut
from app.services.ingestion import latest_successful_run

router = APIRouter(prefix="/investors", tags=["investors"])


def _is_stale(entity_last_seen, latest_run: IngestionRun | None) -> bool:
    if latest_run is None or latest_run.finished_at is None:
        return False
    if entity_last_seen is None:
        return True
    return entity_last_seen < latest_run.finished_at


def _to_out(investor: Investor, *, latest_run: IngestionRun | None = None) -> InvestorOut:
    return InvestorOut(
        id=investor.id,
        name=investor.name,
        investor_type=investor.investor_type,
        check_size_min=investor.check_size_min,
        check_size_max=investor.check_size_max,
        requirements=investor.requirements,
        website=investor.website,
        logo_url=investor.logo_url,
        locations=[row.location for row in investor.locations],
        industries=[row.industry for row in investor.industries],
        stages=[row.stage for row in investor.stages],
        created_at=investor.created_at,
        updated_at=investor.updated_at,
        last_seen_at=investor.last_seen_at,
        last_ingestion_run_id=investor.last_ingestion_run_id,
        stale=_is_stale(investor.last_seen_at, latest_run),
    )


@router.get("", response_model=list[InvestorOut])
def list_investors(
    q: str | None = Query(None, description="Search by investor name"),
    location: str | None = Query(None, description="Filter by location"),
    industry: str | None = Query(None, description="Filter by industry"),
    stage: str | None = Query(None, description="Filter by funding stage"),
    stale: bool = Query(False, description="Only investors not seen in the latest successful ingest"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    latest_run = latest_successful_run(db, "investors")
    stmt = select(Investor).options(
        selectinload(Investor.locations),
        selectinload(Investor.industries),
        selectinload(Investor.stages),
    )
    if q:
        stmt = stmt.where(Investor.name.ilike(f"%{q}%"))
    if location:
        stmt = stmt.where(Investor.locations.any(location=location))
    if industry:
        stmt = stmt.where(Investor.industries.any(industry=industry))
    if stage:
        stmt = stmt.where(Investor.stages.any(stage=stage))
    if stale and latest_run and latest_run.finished_at:
        stmt = stmt.where(
            (Investor.last_seen_at.is_(None)) | (Investor.last_seen_at < latest_run.finished_at)
        )
    stmt = stmt.order_by(Investor.name).offset(offset).limit(limit)
    investors = db.scalars(stmt).all()
    return [_to_out(inv, latest_run=latest_run) for inv in investors]


@router.get("/{investor_id}", response_model=InvestorOut)
def get_investor(investor_id: int, db: Session = Depends(get_db)):
    stmt = (
        select(Investor)
        .where(Investor.id == investor_id)
        .options(
            selectinload(Investor.locations),
            selectinload(Investor.industries),
            selectinload(Investor.stages),
        )
    )
    investor = db.scalar(stmt)
    if investor is None:
        raise HTTPException(status_code=404, detail="Investor not found")
    return _to_out(investor, latest_run=latest_successful_run(db, "investors"))
