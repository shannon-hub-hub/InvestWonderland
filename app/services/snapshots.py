from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.models import Investor, InvestorSnapshot, Startup, StartupSnapshot


def write_investor_snapshots(session: Session, ingestion_run_id: int, investors: list[Investor]) -> int:
    count = 0
    for investor in investors:
        session.add(
            InvestorSnapshot(
                ingestion_run_id=ingestion_run_id,
                investor_id=investor.id,
                name=investor.name,
                website=investor.website,
                investor_type=investor.investor_type,
                check_size_min=investor.check_size_min,
                check_size_max=investor.check_size_max,
                requirements=investor.requirements,
                logo_url=investor.logo_url,
                locations=sorted(row.location for row in investor.locations),
                industries=sorted(row.industry for row in investor.industries),
                stages=sorted(row.stage for row in investor.stages),
            )
        )
        count += 1
    return count


def write_startup_snapshots(session: Session, ingestion_run_id: int, startups: list[Startup]) -> int:
    count = 0
    for startup in startups:
        session.add(
            StartupSnapshot(
                ingestion_run_id=ingestion_run_id,
                startup_id=startup.id,
                name=startup.name,
                website=startup.website,
                description=startup.description,
                logo_url=startup.logo_url,
            )
        )
        count += 1
    return count


def list_investor_snapshots(
    session: Session,
    *,
    ingestion_run_id: int | None = None,
    investor_id: int | None = None,
    limit: int = 100,
) -> list[InvestorSnapshot]:
    stmt = select(InvestorSnapshot).order_by(desc(InvestorSnapshot.snapshotted_at)).limit(limit)
    if ingestion_run_id is not None:
        stmt = stmt.where(InvestorSnapshot.ingestion_run_id == ingestion_run_id)
    if investor_id is not None:
        stmt = stmt.where(InvestorSnapshot.investor_id == investor_id)
    return list(session.scalars(stmt).all())


def list_startup_snapshots(
    session: Session,
    *,
    ingestion_run_id: int | None = None,
    startup_id: int | None = None,
    limit: int = 100,
) -> list[StartupSnapshot]:
    stmt = select(StartupSnapshot).order_by(desc(StartupSnapshot.snapshotted_at)).limit(limit)
    if ingestion_run_id is not None:
        stmt = stmt.where(StartupSnapshot.ingestion_run_id == ingestion_run_id)
    if startup_id is not None:
        stmt = stmt.where(StartupSnapshot.startup_id == startup_id)
    return list(session.scalars(stmt).all())
