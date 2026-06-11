"""Shared scrape → upsert → snapshot path for pipeline and briefing."""

import logging

from sqlalchemy.orm import Session

from app.config import settings
from app.services.ingestion import complete_run, has_running_ingestion, start_run
from app.services.loader import upsert_investors, upsert_startups

logger = logging.getLogger(__name__)


def ingest_investors(session: Session) -> tuple[list[dict], int]:
    """Scrape OpenVC, upsert with snapshots, return (records, run_id)."""
    run = start_run(session, "investors")
    scraped = 0
    upserted = 0
    data: list[dict] = []
    try:
        from app.etl.sources import investors as investors_source

        data = investors_source.scrape(max_pages=settings.ingest_max_pages)
        scraped = len(data)
        upserted = upsert_investors(session, data, ingestion_run_id=run.id)
        complete_run(
            session,
            run,
            status="success",
            records_scraped=scraped,
            records_upserted=upserted,
        )
        logger.info("Investor ingest finished: scraped=%s upserted=%s", scraped, upserted)
        return data, run.id
    except Exception as exc:
        complete_run(
            session,
            run,
            status="failed",
            records_scraped=scraped,
            records_upserted=upserted,
            error_message=str(exc),
        )
        logger.exception("Investor ingest failed")
        raise


def ingest_startups(session: Session) -> tuple[list[dict], int]:
    """Scrape startups.gallery, upsert with snapshots, return (records, run_id)."""
    run = start_run(session, "startups")
    scraped = 0
    upserted = 0
    data: list[dict] = []
    try:
        from app.etl.sources import startups as startups_source

        data = startups_source.scrape()
        scraped = len(data)
        upserted = upsert_startups(session, data, ingestion_run_id=run.id)
        complete_run(
            session,
            run,
            status="success",
            records_scraped=scraped,
            records_upserted=upserted,
        )
        logger.info("Startup ingest finished: scraped=%s upserted=%s", scraped, upserted)
        return data, run.id
    except Exception as exc:
        complete_run(
            session,
            run,
            status="failed",
            records_scraped=scraped,
            records_upserted=upserted,
            error_message=str(exc),
        )
        logger.exception("Startup ingest failed")
        raise


def ingest_investors_if_idle(session: Session) -> list[dict] | None:
    """Run full investor ingest, or None if a job is already running."""
    if has_running_ingestion(session, "investors"):
        return None
    data, _ = ingest_investors(session)
    return data


def ingest_startups_if_idle(session: Session) -> list[dict] | None:
    """Run full startup ingest, or None if a job is already running."""
    if has_running_ingestion(session, "startups"):
        return None
    data, _ = ingest_startups(session)
    return data
