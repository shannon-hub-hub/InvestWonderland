from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analytics import CooccurrenceOut, FundingFlowOut
from app.services.funding_flow import cooccurrence_analytics, funding_flow

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/funding-flow", response_model=FundingFlowOut)
def get_funding_flow(db: Session = Depends(get_db)):
    """Funding focus by sector and stage, plus sector×stage flow matrix rows."""
    return funding_flow(db)


@router.get("/cooccurrence", response_model=CooccurrenceOut)
def get_cooccurrence(
    limit: int = Query(25, ge=1, le=100, description="Max pairs per section"),
    min_shared: int = Query(1, ge=1, le=10, description="Min shared tags for investor pairs"),
    db: Session = Depends(get_db),
):
    """Industry/stage tag pairs and investor pairs with overlapping focus."""
    return cooccurrence_analytics(db, limit=limit, min_shared=min_shared)
