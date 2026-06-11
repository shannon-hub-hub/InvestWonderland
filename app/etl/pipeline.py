import logging

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.ingest_source import ingest_investors, ingest_startups

logger = logging.getLogger(__name__)

SOURCES = ("investors", "startups", "all")


def run_source(session: Session, source: str) -> int:
    if source == "investors":
        _, run_id = ingest_investors(session)
        return run_id
    if source == "startups":
        _, run_id = ingest_startups(session)
        return run_id
    raise ValueError(f"Unknown source: {source}")


def run_pipeline(source: str) -> list[int]:
    if source not in SOURCES:
        raise ValueError(f"source must be one of {SOURCES}")

    targets = ["investors", "startups"] if source == "all" else [source]
    run_ids: list[int] = []

    with SessionLocal() as session:
        for target in targets:
            try:
                run_ids.append(run_source(session, target))
            except Exception:
                if source != "all":
                    raise

    return run_ids
