from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InvestorSnapshotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ingestion_run_id: int
    investor_id: int | None
    name: str
    website: str
    investor_type: str | None
    check_size_min: int | None
    check_size_max: int | None
    requirements: str | None
    logo_url: str | None
    locations: list[str]
    industries: list[str]
    stages: list[str]
    snapshotted_at: datetime


class StartupSnapshotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ingestion_run_id: int
    startup_id: int | None
    name: str
    website: str
    description: str | None
    logo_url: str | None
    snapshotted_at: datetime
