from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StartupOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    website: str
    logo_url: str | None
    created_at: datetime
    updated_at: datetime
    last_seen_at: datetime | None
    last_ingestion_run_id: int | None
    stale: bool = False
