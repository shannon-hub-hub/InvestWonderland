from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class IngestionSource(str, Enum):
    investors = "investors"
    startups = "startups"
    all = "all"


class IngestionRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    status: str
    started_at: datetime
    finished_at: datetime | None
    records_scraped: int
    records_upserted: int
    error_message: str | None


class IngestionTriggerOut(BaseModel):
    source: IngestionSource
    run_ids: list[int] = Field(description="IDs of created ingestion_runs rows")
    message: str


class ScrapeStatsOut(BaseModel):
    investors_scraped: int = Field(description="Count of successful OpenVC rescrape runs")
    startups_scraped: int = Field(description="Count of successful gallery rescrape runs")
