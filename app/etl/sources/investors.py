from app.config import settings
from app.etl.browser import init_driver
from invest_scraper import scrape_investors as _scrape_investors


def scrape(max_pages: int | None = None) -> list[dict]:
    pages = max_pages if max_pages is not None else settings.ingest_max_pages
    driver = init_driver()
    try:
        return _scrape_investors(driver, max_pages=pages, limit=None)
    finally:
        driver.quit()
