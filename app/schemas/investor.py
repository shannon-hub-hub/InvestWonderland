from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InvestorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    investor_type: str | None
    check_size_min: int | None
    check_size_max: int | None
    requirements: str | None
    website: str
    logo_url: str | None
    locations: list[str]
    industries: list[str]
    stages: list[str]
    created_at: datetime
    updated_at: datetime
    last_seen_at: datetime | None
    last_ingestion_run_id: int | None
    stale: bool = False
