"""Funding-flow analytics: sector, stage, and investor co-occurrence from OpenVC data."""

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session, aliased

from app.db.models import Investor, InvestorIndustry, InvestorLocation, InvestorStage, Startup


def _investor_tag_counts(session: Session, join_model, label_attr: str, *, limit: int) -> list[dict]:
    label_col = getattr(join_model, label_attr)
    rows = session.execute(
        select(label_col, func.count(func.distinct(Investor.id)).label("count"))
        .join(Investor, join_model.investor_id == Investor.id)
        .group_by(label_col)
        .order_by(func.count(func.distinct(Investor.id)).desc())
        .limit(limit)
    ).all()
    return [{"name": str(r[0]), "count": int(r[1])} for r in rows if r[0]]


def _sector_counts(session: Session, *, limit: int = 20) -> list[dict]:
    rows = session.execute(
        select(InvestorIndustry.industry, func.count(func.distinct(InvestorIndustry.investor_id)).label("count"))
        .group_by(InvestorIndustry.industry)
        .order_by(func.count(func.distinct(InvestorIndustry.investor_id)).desc())
        .limit(limit)
    ).all()
    return [{"sector": str(r[0]), "count": int(r[1])} for r in rows if r[0]]


def _stage_counts(session: Session, *, limit: int = 15) -> list[dict]:
    rows = session.execute(
        select(InvestorStage.stage, func.count(func.distinct(InvestorStage.investor_id)).label("count"))
        .group_by(InvestorStage.stage)
        .order_by(func.count(func.distinct(InvestorStage.investor_id)).desc())
        .limit(limit)
    ).all()
    return [{"stage": str(r[0]), "count": int(r[1])} for r in rows if r[0]]


def sector_stage_flow(session: Session, *, limit: int = 100) -> list[dict]:
    """Investor count per sector × stage pair (funding-focus flow)."""
    rows = session.execute(
        select(
            InvestorIndustry.industry.label("sector"),
            InvestorStage.stage.label("stage"),
            func.count(func.distinct(Investor.id)).label("count"),
        )
        .select_from(Investor)
        .join(InvestorIndustry, Investor.id == InvestorIndustry.investor_id)
        .join(InvestorStage, Investor.id == InvestorStage.investor_id)
        .group_by(InvestorIndustry.industry, InvestorStage.stage)
        .order_by(func.count(func.distinct(Investor.id)).desc())
        .limit(limit)
    ).all()
    return [
        {"sector": str(r.sector), "stage": str(r.stage), "count": int(r.count)}
        for r in rows
        if r.sector and r.stage
    ]


def startup_stage_flow(session: Session) -> list[dict]:
    """Gallery startups grouped by scrape category (stage proxy)."""
    count = int(session.scalar(select(func.count(Startup.id))) or 0)
    if count == 0:
        return []
    return [{"stage": "Series C+", "count": count}]


def funding_flow(session: Session) -> dict:
    investor_count = int(session.scalar(select(func.count(Investor.id))) or 0)
    startup_count = int(session.scalar(select(func.count(Startup.id))) or 0)
    type_rows = session.execute(
        select(Investor.investor_type, func.count(Investor.id).label("count"))
        .where(Investor.investor_type.isnot(None), Investor.investor_type != "")
        .group_by(Investor.investor_type)
        .order_by(func.count(Investor.id).desc())
        .limit(10)
    ).all()
    return {
        "investor_count": investor_count,
        "startup_count": startup_count,
        "by_sector": _sector_counts(session),
        "by_stage": _stage_counts(session),
        "by_location": _investor_tag_counts(session, InvestorLocation, "location", limit=10),
        "by_type": [{"name": str(r[0]), "count": int(r[1])} for r in type_rows if r[0]],
        "sector_stage_flow": sector_stage_flow(session),
        "startup_stage_flow": startup_stage_flow(session),
    }


def _tag_pair_cooccurrence(
    session: Session,
    model,
    attr: str,
    *,
    limit: int = 25,
) -> list[dict]:
    left = aliased(model)
    right = aliased(model)
    label = getattr(left, attr)
    label_b = getattr(right, attr)
    rows = session.execute(
        select(
            label.label("tag_a"),
            label_b.label("tag_b"),
            func.count(func.distinct(left.investor_id)).label("count"),
        )
        .select_from(left)
        .join(
            right,
            and_(
                left.investor_id == right.investor_id,
                label < label_b,
            ),
        )
        .group_by(label, label_b)
        .order_by(func.count(func.distinct(left.investor_id)).desc())
        .limit(limit)
    ).all()
    return [
        {"tag_a": str(r.tag_a), "tag_b": str(r.tag_b), "investor_count": int(r.count)}
        for r in rows
        if r.tag_a and r.tag_b
    ]


def investor_cooccurrence(session: Session, *, limit: int = 25, min_shared: int = 1) -> list[dict]:
    """Top investor pairs ranked by shared industry tags."""
    left = aliased(InvestorIndustry)
    right = aliased(InvestorIndustry)
    inv_a = aliased(Investor)
    inv_b = aliased(Investor)

    rows = session.execute(
        select(
            inv_a.name.label("investor_a"),
            inv_b.name.label("investor_b"),
            func.count().label("shared_industries"),
        )
        .select_from(left)
        .join(
            right,
            and_(
                left.investor_id < right.investor_id,
                left.industry == right.industry,
            ),
        )
        .join(inv_a, inv_a.id == left.investor_id)
        .join(inv_b, inv_b.id == right.investor_id)
        .group_by(inv_a.name, inv_b.name)
        .having(func.count() >= min_shared)
        .order_by(func.count().desc())
        .limit(limit)
    ).all()

    return [
        {
            "investor_a": r.investor_a,
            "investor_b": r.investor_b,
            "shared_industries": int(r.shared_industries),
        }
        for r in rows
    ]


def cooccurrence_analytics(session: Session, *, limit: int = 25, min_shared: int = 1) -> dict:
    return {
        "industry_pairs": _tag_pair_cooccurrence(
            session, InvestorIndustry, "industry", limit=limit
        ),
        "stage_pairs": _tag_pair_cooccurrence(session, InvestorStage, "stage", limit=limit),
        "investor_pairs": investor_cooccurrence(session, limit=limit, min_shared=min_shared),
    }
