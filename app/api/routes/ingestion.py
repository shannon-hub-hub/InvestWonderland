import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.etl.pipeline import run_pipeline
from app.schemas.ingestion import IngestionRunOut, IngestionSource, IngestionTriggerOut, ScrapeStatsOut
from app.schemas.snapshots import InvestorSnapshotOut, StartupSnapshotOut
from app.services.ingestion import get_run, has_running_ingestion, list_runs, scrape_stats
from app.services.snapshots import list_investor_snapshots, list_startup_snapshots

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ingestion", tags=["ingestion"])


def _run_in_background(source: str) -> None:
    try:
        run_pipeline(source)
    except Exception:
        logger.exception("Background ingestion failed for source=%s", source)


@router.get("/stats", response_model=ScrapeStatsOut)
def get_scrape_stats(db: Session = Depends(get_db)):
    """How many times each rescrape job has completed successfully."""
    return scrape_stats(db)


@router.post("/runs", response_model=IngestionTriggerOut, status_code=202)
def trigger_ingestion(
    source: IngestionSource,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Queue a full re-ingestion job (runs in the API process background)."""
    if source.value in ("investors", "startups") and has_running_ingestion(db, source.value):
        raise HTTPException(
            status_code=409,
            detail=f"Ingestion for '{source.value}' is already in progress",
        )

    if source.value == "all":
        for src in ("investors", "startups"):
            if has_running_ingestion(db, src):
                raise HTTPException(
                    status_code=409,
                    detail=f"Ingestion for '{src}' is already in progress",
                )

    background_tasks.add_task(_run_in_background, source.value)
    return IngestionTriggerOut(
        source=source,
        run_ids=[],
        message=f"Scraping all available {source.value} records from the website. Poll GET /api/v1/ingestion/runs for status.",
    )


@router.get("/runs", response_model=list[IngestionRunOut])
def get_ingestion_runs(
    source: IngestionSource | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return list_runs(db, source=source.value if source else None, limit=limit)


@router.get("/runs/{run_id}", response_model=IngestionRunOut)
def get_ingestion_run(run_id: int, db: Session = Depends(get_db)):
    run = get_run(db, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Ingestion run not found")
    return run


@router.get("/runs/{run_id}/snapshots/investors", response_model=list[InvestorSnapshotOut])
def get_investor_snapshots_for_run(
    run_id: int,
    limit: int = Query(500, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    """Historical investor state captured during a specific ingestion run."""
    if get_run(db, run_id) is None:
        raise HTTPException(status_code=404, detail="Ingestion run not found")
    return list_investor_snapshots(db, ingestion_run_id=run_id, limit=limit)


@router.get("/runs/{run_id}/snapshots/startups", response_model=list[StartupSnapshotOut])
def get_startup_snapshots_for_run(
    run_id: int,
    limit: int = Query(500, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    """Historical startup state captured during a specific ingestion run."""
    if get_run(db, run_id) is None:
        raise HTTPException(status_code=404, detail="Ingestion run not found")
    return list_startup_snapshots(db, ingestion_run_id=run_id, limit=limit)


@router.get("/snapshots/investors", response_model=list[InvestorSnapshotOut])
def get_investor_snapshot_history(
    investor_id: int = Query(..., ge=1),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Longitudinal history for one investor across ingestion runs."""
    return list_investor_snapshots(db, investor_id=investor_id, limit=limit)


@router.get("/snapshots/startups", response_model=list[StartupSnapshotOut])
def get_startup_snapshot_history(
    startup_id: int = Query(..., ge=1),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Longitudinal history for one startup across ingestion runs."""
    return list_startup_snapshots(db, startup_id=startup_id, limit=limit)
