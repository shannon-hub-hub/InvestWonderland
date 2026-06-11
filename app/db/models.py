from datetime import date, datetime

from sqlalchemy import BigInteger, Date, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Investor(Base):
    __tablename__ = "investors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    investor_type: Mapped[str | None] = mapped_column(String(128))
    check_size_min: Mapped[int | None] = mapped_column(BigInteger)
    check_size_max: Mapped[int | None] = mapped_column(BigInteger)
    requirements: Mapped[str | None] = mapped_column(Text)
    website: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    logo_url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    last_seen_at: Mapped[datetime | None] = mapped_column()
    last_ingestion_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("ingestion_runs.id", ondelete="SET NULL")
    )

    locations: Mapped[list["InvestorLocation"]] = relationship(back_populates="investor", cascade="all, delete-orphan")
    industries: Mapped[list["InvestorIndustry"]] = relationship(back_populates="investor", cascade="all, delete-orphan")
    stages: Mapped[list["InvestorStage"]] = relationship(back_populates="investor", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("name", "website"),)


class InvestorLocation(Base):
    __tablename__ = "investor_locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    investor_id: Mapped[int] = mapped_column(ForeignKey("investors.id", ondelete="CASCADE"), nullable=False)
    location: Mapped[str] = mapped_column(String(256), nullable=False)
    investor: Mapped[Investor] = relationship(back_populates="locations")
    __table_args__ = (UniqueConstraint("investor_id", "location"),)


class InvestorIndustry(Base):
    __tablename__ = "investor_industries"

    id: Mapped[int] = mapped_column(primary_key=True)
    investor_id: Mapped[int] = mapped_column(ForeignKey("investors.id", ondelete="CASCADE"), nullable=False)
    industry: Mapped[str] = mapped_column(String(256), nullable=False)
    investor: Mapped[Investor] = relationship(back_populates="industries")
    __table_args__ = (UniqueConstraint("investor_id", "industry"),)


class InvestorStage(Base):
    __tablename__ = "investor_stages"

    id: Mapped[int] = mapped_column(primary_key=True)
    investor_id: Mapped[int] = mapped_column(ForeignKey("investors.id", ondelete="CASCADE"), nullable=False)
    stage: Mapped[str] = mapped_column(String(128), nullable=False)
    investor: Mapped[Investor] = relationship(back_populates="stages")
    __table_args__ = (UniqueConstraint("investor_id", "stage"),)


class Startup(Base):
    __tablename__ = "startups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    website: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    logo_url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    last_seen_at: Mapped[datetime | None] = mapped_column()
    last_ingestion_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("ingestion_runs.id", ondelete="SET NULL")
    )
    __table_args__ = (UniqueConstraint("name", "website"),)


class DailyBriefing(Base):
    __tablename__ = "daily_briefings"

    id: Mapped[int] = mapped_column(primary_key=True)
    briefing_date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    lookback_days: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(server_default=func.now())


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    started_at: Mapped[datetime] = mapped_column(server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column()
    records_scraped: Mapped[int] = mapped_column(default=0)
    records_upserted: Mapped[int] = mapped_column(default=0)
    error_message: Mapped[str | None] = mapped_column(Text)

    investor_snapshots: Mapped[list["InvestorSnapshot"]] = relationship(back_populates="ingestion_run")
    startup_snapshots: Mapped[list["StartupSnapshot"]] = relationship(back_populates="ingestion_run")


class InvestorSnapshot(Base):
    __tablename__ = "investor_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    ingestion_run_id: Mapped[int] = mapped_column(
        ForeignKey("ingestion_runs.id", ondelete="CASCADE"), nullable=False
    )
    investor_id: Mapped[int | None] = mapped_column(ForeignKey("investors.id", ondelete="SET NULL"))
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    website: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    investor_type: Mapped[str | None] = mapped_column(String(128))
    check_size_min: Mapped[int | None] = mapped_column(BigInteger)
    check_size_max: Mapped[int | None] = mapped_column(BigInteger)
    requirements: Mapped[str | None] = mapped_column(Text)
    logo_url: Mapped[str | None] = mapped_column(Text)
    locations: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    industries: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    stages: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    snapshotted_at: Mapped[datetime] = mapped_column(server_default=func.now())

    ingestion_run: Mapped[IngestionRun] = relationship(back_populates="investor_snapshots")


class StartupSnapshot(Base):
    __tablename__ = "startup_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    ingestion_run_id: Mapped[int] = mapped_column(
        ForeignKey("ingestion_runs.id", ondelete="CASCADE"), nullable=False
    )
    startup_id: Mapped[int | None] = mapped_column(ForeignKey("startups.id", ondelete="SET NULL"))
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    website: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    description: Mapped[str | None] = mapped_column(Text)
    logo_url: Mapped[str | None] = mapped_column(Text)
    snapshotted_at: Mapped[datetime] = mapped_column(server_default=func.now())

    ingestion_run: Mapped[IngestionRun] = relationship(back_populates="startup_snapshots")
