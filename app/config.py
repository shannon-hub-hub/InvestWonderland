from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://postgres:password@localhost:5433/scraper"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    feed_lookback_days: int = 30
    startups_gallery_url: str = "https://startups.gallery/categories/stages/series-c"
    ingest_max_pages: int = 50
    headless: bool = True
    api_title: str = "Invest Wonderland API"
    api_version: str = "1.0.0"
    app_tagline: str = (
        "The daily briefing for investors who discover deals through product momentum — not just press releases."
    )
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"


settings = Settings()
