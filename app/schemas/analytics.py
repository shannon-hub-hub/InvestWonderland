from pydantic import BaseModel, Field


class CountBucket(BaseModel):
    count: int


class SectorBucket(CountBucket):
    sector: str


class StageBucket(CountBucket):
    stage: str


class NameBucket(CountBucket):
    name: str


class SectorStageFlow(BaseModel):
    sector: str
    stage: str
    count: int


class TagPairCooccurrence(BaseModel):
    tag_a: str
    tag_b: str
    investor_count: int


class InvestorPairCooccurrence(BaseModel):
    investor_a: str
    investor_b: str
    shared_industries: int


class FundingFlowOut(BaseModel):
    investor_count: int
    startup_count: int
    by_sector: list[SectorBucket]
    by_stage: list[StageBucket]
    by_location: list[NameBucket]
    by_type: list[NameBucket]
    sector_stage_flow: list[SectorStageFlow]
    startup_stage_flow: list[StageBucket] = Field(
        description="Gallery companies by stage category (from scrape URL)"
    )


class CooccurrenceOut(BaseModel):
    industry_pairs: list[TagPairCooccurrence]
    stage_pairs: list[TagPairCooccurrence]
    investor_pairs: list[InvestorPairCooccurrence]
