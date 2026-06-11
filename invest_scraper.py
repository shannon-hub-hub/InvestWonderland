import time
import csv
import os
import random
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def init_driver():
    from app.etl.browser import init_driver as _init

    return _init()


def scrape_investors(driver, max_pages: int | None = None, limit: int | None = None):
    results = []
    page_num = 1
    max_pages = max_pages or int(os.getenv("INGEST_MAX_PAGES", "50"))

    while page_num <= max_pages:
        if limit is not None and len(results) >= limit:
            break
        # Load page directly via URL
        url = f"https://www.openvc.app/search?page={page_num}"
        print(f"\n{'='*60}")
        print(f"Loading page {page_num}: {url}")
        print(f"{'='*60}")
        
        driver.get(url)
        
        # Random delay to avoid CAPTCHA - looks more human
        delay = random.uniform(4, 8)
        print(f"Waiting {delay:.1f} seconds...")
        time.sleep(delay)
        
        # Wait for table
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
            )
        except:
            print(f"⚠️  No table found on page {page_num}, stopping")
            break
        
        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        print(f"Found {len(rows)} rows on this page")
        
        # Check if page is empty
        if len(rows) == 0:
            print(f"No rows found on page {page_num}, stopping")
            break
        
        valid_rows = 0
        
        for i, row in enumerate(rows):
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                
                # Skip if not enough cells (like ad rows)
                if len(cells) < 5:
                    continue
                
                # Cell 0: Logo
                logo_url = ""
                try:
                    img_elem = cells[0].find_element(By.TAG_NAME, "img")
                    logo_url = img_elem.get_attribute("src")
                except:
                    pass
                
                # Cell 1: Name and Type
                name_cell_text = cells[1].text.strip().split("\n")
                investor_name = name_cell_text[0] if len(name_cell_text) > 0 else ""
                investor_type = name_cell_text[1] if len(name_cell_text) > 1 else ""
                
                # Skip if no name
                if not investor_name:
                    continue
                
                # Cell 2: Countries/Locations
                locations = cells[2].text.strip().replace("\n", ", ")
                
                # Cell 3: Check Size
                check_size_raw = cells[3].text.strip()
                check_min, check_max = "", ""
                if "to" in check_size_raw:
                    parts = check_size_raw.replace("$", "").replace("k", "000").replace("M", "000000").split("to")
                    check_min = parts[0].strip()
                    check_max = parts[1].strip()
                else:
                    check_min = check_size_raw
                
                # Cell 4: Stage
                stage = cells[4].text.strip().replace("\n", ", ")
                
                # Cell 5: Requirements/Description
                requirements = cells[5].text.strip() if len(cells) > 5 else ""
                
                # Cell 6: Industries
                industries = cells[6].text.strip() if len(cells) > 6 else ""
                
                # Cell 7: Website link
                website = ""
                try:
                    if len(cells) > 7:
                        website_elem = cells[7].find_element(By.TAG_NAME, "a")
                        website = website_elem.get_attribute("href")
                except:
                    pass
                
                results.append({
                    'name': investor_name,
                    'type': investor_type,
                    'locations': locations,
                    'check_min': check_min,
                    'check_max': check_max,
                    'stage': stage,
                    'requirements': requirements,
                    'industries': industries,
                    'website': website,
                    'logo_url': logo_url
                })

                if limit is not None and len(results) >= limit:
                    break

                print(f"✓ Row {i}: {investor_name}")
                valid_rows += 1
                
            except Exception as e:
                print(f"✗ Error on row {i}: {e}")
                continue
        
        if valid_rows == 0:
            print(f"No valid investors found on page {page_num}, stopping")
            break
        
        print(f"Scraped {valid_rows} investors from this page")
        print(f"Total investors scraped so far: {len(results)}")
        
        # Move to next page
        page_num += 1

    if limit is not None:
        return results[:limit]
    return results

def save_csv(data, filename="openvc_investors.csv"):
    if not data:
        print("No data to save!")
        return
    
    downloads = os.path.join(os.path.expanduser("~"), "Downloads")
    filepath = os.path.join(downloads, filename)
    
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Investor_Name",
            "Type",
            "Locations",
            "Check_Size_Min",
            "Check_Size_Max",
            "Stage",
            "Requirements",
            "Industries",
            "Website",
            "Logo_URL"
        ])
        
        for row in data:
            writer.writerow([
                row['name'],
                row['type'],
                row['locations'],
                row['check_min'],
                row['check_max'],
                row['stage'],
                row['requirements'],
                row['industries'],
                row['website'],
                row['logo_url']
            ])
    
    print(f"\n✅ SUCCESS! Saved {len(data)} investors to: {filepath}")


def save_to_db(data):
    if not data:
        return
    from app.db.session import SessionLocal
    from app.services.loader import upsert_investors

    with SessionLocal() as session:
        count = upsert_investors(session, data)
    print(f"✅ Saved {count} investors to PostgreSQL")


def main():
    driver = init_driver()
    data = []
    try:
        print("Starting scraper...")
        print("This will scrape multiple pages - it may take several minutes")
        print("Press Ctrl+C to stop early if needed\n")
        
        data = scrape_investors(driver)
        save_csv(data)
        save_to_db(data)
        
        print("\n" + "="*80)
        print(f"🎉 COMPLETE! Scraped {len(data)} investors successfully!")
        print("="*80)
        
        time.sleep(3)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
        if data:
            print(f"Saving {len(data)} investors collected so far...")
            save_csv(data)
            save_to_db(data)
    except Exception as e:
        print(f"Error: {e}")
        if data:
            print(f"Saving {len(data)} investors collected before error...")
            save_csv(data)
            save_to_db(data)
    finally:
        driver.quit()
        print("Browser closed.")

if __name__ == "__main__":
    main()