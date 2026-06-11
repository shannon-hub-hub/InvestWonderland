import re
from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy import delete, func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.db.models import (
    Investor,
    InvestorIndustry,
    InvestorLocation,
    InvestorStage,
    Startup,
)
from app.services.snapshots import write_investor_snapshots, write_startup_snapshots


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _split_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in re.split(r"[,;]", value) if part.strip()]


def _parse_amount(value: str | None) -> int | None:
    if not value:
        return None
    cleaned = re.sub(r"[^\d]", "", str(value))
    if not cleaned:
        return None
    try:
        return int(cleaned)
    except ValueError:
        return None


def _dedupe_records(records: Iterable[dict], *key_fields: str) -> list[dict]:
    """Last scraped row wins for each composite natural key within a batch."""
    seen: dict[tuple[str, ...], dict] = {}
    for record in records:
        key = tuple((record.get(field) or "").strip() for field in key_fields)
        if not key[0]:
            continue
        seen[key] = record
    return list(seen.values())


def _seen_fields(ingestion_run_id: int | None) -> tuple[dict, dict]:
    """Return (insert values, update fields) for last-seen tracking."""
    seen_at = _utcnow()
    values: dict = {"last_seen_at": seen_at}
    update: dict = {"last_seen_at": seen_at}
    if ingestion_run_id is not None:
        values["last_ingestion_run_id"] = ingestion_run_id
        update["last_ingestion_run_id"] = ingestion_run_id
    return values, update


def _sync_child_rows(
    session: Session,
    investor_id: int,
    values: list[str],
    model,
    attr: str,
) -> None:
    incoming = set(values)
    col = getattr(model, attr)

    if not incoming:
        session.execute(delete(model).where(model.investor_id == investor_id))
        return

    session.execute(
        delete(model).where(
            model.investor_id == investor_id,
            col.not_in(incoming),
        )
    )

    for value in incoming:
        session.execute(
            pg_insert(model)
            .values(investor_id=investor_id, **{attr: value})
            .on_conflict_do_nothing(index_elements=["investor_id", attr])
        )


def _upsert_investor(session: Session, record: dict, *, ingestion_run_id: int | None) -> Investor | None:
    name = (record.get("name") or "").strip()
    if not name:
        return None
    website = (record.get("website") or "").strip()

    seen_values, seen_update = _seen_fields(ingestion_run_id)
    values = {
        "name": name,
        "website": website,
        "investor_type": (record.get("type") or "").strip() or None,
        "check_size_min": _parse_amount(record.get("check_min")),
        "check_size_max": _parse_amount(record.get("check_max")),
        "requirements": (record.get("requirements") or "").strip() or None,
        "logo_url": (record.get("logo_url") or "").strip() or None,
        **seen_values,
    }
    update = {
        "investor_type": values["investor_type"],
        "check_size_min": values["check_size_min"],
        "check_size_max": values["check_size_max"],
        "requirements": values["requirements"],
        "logo_url": values["logo_url"],
        **seen_update,
        "updated_at": func.now(),
    }

    investor = session.scalar(
        pg_insert(Investor)
        .values(**values)
        .on_conflict_do_update(index_elements=["name", "website"], set_=update)
        .returning(Investor)
    )
    if investor is None:
        return None

    _sync_child_rows(
        session,
        investor.id,
        _split_list(record.get("locations")),
        InvestorLocation,
        "location",
    )
    _sync_child_rows(
        session,
        investor.id,
        _split_list(record.get("industries")),
        InvestorIndustry,
        "industry",
    )
    _sync_child_rows(
        session,
        investor.id,
        _split_list(record.get("stage")),
        InvestorStage,
        "stage",
    )
    session.refresh(investor, attribute_names=["locations", "industries", "stages"])
    return investor


def _upsert_startup(session: Session, record: dict, *, ingestion_run_id: int | None) -> Startup | None:
    name = (record.get("name") or "").strip()
    if not name:
        return None
    website = (record.get("website") or "").strip()

    seen_values, seen_update = _seen_fields(ingestion_run_id)
    values = {
        "name": name,
        "website": website,
        "description": (record.get("description") or "").strip() or None,
        "logo_url": (record.get("logo_url") or "").strip() or None,
        **seen_values,
    }
    update = {
        "description": values["description"],
        "logo_url": values["logo_url"],
        **seen_update,
        "updated_at": func.now(),
    }

    return session.scalar(
        pg_insert(Startup)
        .values(**values)
        .on_conflict_do_update(index_elements=["name", "website"], set_=update)
        .returning(Startup)
    )


def upsert_investors(
    session: Session,
    records: Iterable[dict],
    *,
    ingestion_run_id: int | None = None,
) -> int:
    saved: list[Investor] = []
    for record in _dedupe_records(records, "name", "website"):
        investor = _upsert_investor(session, record, ingestion_run_id=ingestion_run_id)
        if investor is not None:
            saved.append(investor)

    if ingestion_run_id is not None and saved:
        write_investor_snapshots(session, ingestion_run_id, saved)

    session.commit()
    return len(saved)


def upsert_startups(
    session: Session,
    records: Iterable[dict],
    *,
    ingestion_run_id: int | None = None,
) -> int:
    saved: list[Startup] = []
    for record in _dedupe_records(records, "name", "website"):
        startup = _upsert_startup(session, record, ingestion_run_id=ingestion_run_id)
        if startup is not None:
            saved.append(startup)

    if ingestion_run_id is not None and saved:
        write_startup_snapshots(session, ingestion_run_id, saved)

    session.commit()
    return len(saved)
