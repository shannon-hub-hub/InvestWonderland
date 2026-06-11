from app.config import settings
from app.etl.browser import init_driver
from companies_scraper import scrape_investors as _scrape_startups


def scrape() -> list[dict]:
    driver = init_driver()
    try:
        return _scrape_startups(driver, settings.startups_gallery_url, limit=None)
    finally:
        driver.quit()
