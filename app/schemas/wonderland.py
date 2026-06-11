from pydantic import BaseModel


class DailySignal(BaseModel):
    rank: int
    name: str
    slug: str
    tagline: str
    summary: str
    sector: str
    stage: str
    amount_usd: int
    estimated_raise: str
    announced_at: str
    website: str
    logo_url: str | None = None
    source_url: str | None = None
    source: str | None = None
    pick_kind: str | None = None
    locations: str | None = None
    investors: list[str] = []
    verdict: str
    synthesis: str


class WonderlandBriefing(BaseModel):
    date: str
    days: int
    phase: str = "Validation"
    version: str = "1.0"
    one_liner: str
    signals: list[DailySignal]
    ai_enabled: bool = False
    sources: list[str] = []
    pick_count: int = 0
