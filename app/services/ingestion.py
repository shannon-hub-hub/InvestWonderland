from datetime import datetime, timezone

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.db.models import IngestionRun


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def start_run(session: Session, source: str) -> IngestionRun:
    running = session.scalar(
        select(IngestionRun).where(
            IngestionRun.source == source,
            IngestionRun.status == "running",
        )
    )
    if running:
        raise RuntimeError(f"Ingestion for '{source}' is already running (run_id={running.id})")

    run = IngestionRun(source=source, status="running", started_at=utcnow())
    session.add(run)
    session.commit()
    session.refresh(run)
    return run


def complete_run(
    session: Session,
    run: IngestionRun,
    *,
    status: str,
    records_scraped: int,
    records_upserted: int,
    error_message: str | None = None,
) -> IngestionRun:
    run.status = status
    run.finished_at = utcnow()
    run.records_scraped = records_scraped
    run.records_upserted = records_upserted
    run.error_message = error_message
    session.commit()
    session.refresh(run)
    return run


def has_running_ingestion(session: Session, source: str) -> bool:
    running = session.scalar(
        select(IngestionRun).where(
            IngestionRun.source == source,
            IngestionRun.status == "running",
        )
    )
    return running is not None


def get_run(session: Session, run_id: int) -> IngestionRun | None:
    return session.get(IngestionRun, run_id)


def list_runs(session: Session, *, source: str | None = None, limit: int = 20) -> list[IngestionRun]:
    stmt = select(IngestionRun).order_by(desc(IngestionRun.started_at)).limit(limit)
    if source:
        stmt = stmt.where(IngestionRun.source == source)
    return list(session.scalars(stmt).all())


def count_successful_scrapes(session: Session, source: str) -> int:
    """Number of completed rescrape jobs for a source (each button click = one run)."""
    return int(
        session.scalar(
            select(func.count(IngestionRun.id)).where(
                IngestionRun.source == source,
                IngestionRun.status == "success",
            )
        )
        or 0
    )


def scrape_stats(session: Session) -> dict:
    return {
        "investors_scraped": count_successful_scrapes(session, "investors"),
        "startups_scraped": count_successful_scrapes(session, "startups"),
    }


def latest_successful_run(session: Session, source: str) -> IngestionRun | None:
    return session.scalar(
        select(IngestionRun)
        .where(IngestionRun.source == source, IngestionRun.status == "success")
        .order_by(desc(IngestionRun.finished_at))
        .limit(1)
    )
