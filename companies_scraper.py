import time
import csv
import os
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def init_driver():
    from app.etl.browser import init_driver as _init

    return _init()

#Extract
def scroll_and_load_all(driver, max_scrolls=50):
    """Scroll down the page multiple times to load all content"""
    print("\n🔄 Scrolling to load all companies...")
    
    last_height = driver.execute_script("return document.body.scrollHeight")
    cards_count = 0
    no_change_count = 0
    
    for scroll in range(max_scrolls):
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait for new content to load
        time.sleep(random.uniform(1.5, 3))
        
        # Check how many cards we have now
        current_cards = len(driver.find_elements(By.CSS_SELECTOR, "a[href*='/companies/']"))
        
        # Calculate new scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if current_cards > cards_count:
            print(f"Scroll {scroll + 1}: Found {current_cards} companies (loaded {current_cards - cards_count} new)")
            cards_count = current_cards
            no_change_count = 0
        else:
            no_change_count += 1
            print(f"Scroll {scroll + 1}: Still at {cards_count} companies (no new content)")
        
        # If no new content after 3 scrolls, we've probably reached the end
        if no_change_count >= 3:
            print(f"✓ Reached end of page after {scroll + 1} scrolls")
            break
        
        # If page height didn't change, we might be at the bottom
        if new_height == last_height:
            no_change_count += 1
        
        last_height = new_height
    
    # Scroll back to top
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)
    
    print(f"✓ Finished loading. Total companies visible: {cards_count}\n")
    return cards_count

def scrape_investors(driver, url, limit: int | None = None):
    results = []
    
    print(f"\n{'='*60}")
    print(f"Loading: {url}")
    print(f"{'='*60}")
    
    driver.get(url)
    
    # Initial delay
    delay = random.uniform(3, 5)
    print(f"Waiting {delay:.1f} seconds for initial load...")
    time.sleep(delay)
    
    # Scroll to load all content
    scroll_and_load_all(driver, max_scrolls=50)
    
    # Try multiple selectors to find the company cards
    selectors_to_try = [
        "a[href*='/companies/']",
        "a.framer-4z4hpc",
        "a[class*='framer']",
        "div[class*='framer'] a",
        "a h2"
    ]
    
    cards = []
    for selector in selectors_to_try:
        print(f"Trying selector: {selector}")
        try:
            cards = driver.find_elements(By.CSS_SELECTOR, selector)
            if len(cards) > 0:
                print(f"✓ Found {len(cards)} elements with selector: {selector}")
                break
        except:
            print(f"✗ No elements found with selector: {selector}")
            continue
    
    if len(cards) == 0:
        print("\n⚠️  Could not find any company cards with any selector.")
        print("Saving page source to help debug...")
        
        # Save page source for debugging
        debug_file = os.path.join(os.path.expanduser("~"), "Downloads", "page_source.html")
        with open(debug_file, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"Page source saved to: {debug_file}")
        print("Please check this file to see the actual HTML structure.")
        
        return results
    
    # Cards are already the correct <a> elements, no need to transform
    
    print(f"\n📊 Processing {len(cards)} company cards...")
    valid_cards = 0
    
    for i, card in enumerate(cards):
        try:
            # Get the link URL
            company_url = ""
            try:
                company_url = card.get_attribute("href")
            except:
                pass
            
            # Skip if no URL or not a company link
            if not company_url or "/companies/" not in company_url:
                print(f"  ⚠️  Skipping element {i+1}: Not a valid company link")
                continue
            
            # Get company logo
            logo_url = ""
            try:
                img_elem = card.find_element(By.TAG_NAME, "img")
                logo_url = img_elem.get_attribute("src")
            except:
                pass
            
            # Get company name (h2 tag)
            company_name = ""
            try:
                name_elem = card.find_element(By.TAG_NAME, "h2")
                company_name = name_elem.text.strip()
            except:
                # Try getting any text
                company_name = card.text.split("\n")[0].strip() if card.text else ""
            
            # Get description (p tag)
            description = ""
            try:
                desc_elem = card.find_element(By.TAG_NAME, "p")
                description = desc_elem.text.strip()
            except:
                # Try getting second line of text
                text_lines = card.text.split("\n")
                if len(text_lines) > 1:
                    description = text_lines[1].strip()
            
            # Skip if no name
            if not company_name:
                print(f"  ⚠️  Skipping card {i+1}: No company name found")
                continue
            
            results.append({
                'name': company_name,
                'description': description,
                'website': company_url,
                'logo_url': logo_url
            })

            valid_cards += 1

            if limit is not None and valid_cards >= limit:
                break

            if valid_cards % 10 == 0:
                print(f"✓ Processed {valid_cards} companies...")
            
        except Exception as e:
            # Print errors to help debug
            print(f"  ✗ Error on card {i+1}: {e}")
            continue
    
    print(f"\n✅ Successfully scraped {valid_cards} companies!")
    if limit is not None:
        return results[:limit]
    return results

#Load data and save to CSV
def save_csv(data, filename="startups_gallery.csv"):
    if not data:
        print("No data to save!")
        return
    
    downloads = os.path.join(os.path.expanduser("~"), "Downloads")
    filepath = os.path.join(downloads, filename)
    
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Company_Name",
            "Description",
            "Website",
            "Logo_URL"
        ])
        
        for row in data:
            writer.writerow([
                row['name'],
                row['description'],
                row['website'],
                row['logo_url']
            ])
    
    print(f"\n✅ SUCCESS! Saved {len(data)} companies to: {filepath}")


def save_to_db(data):
    if not data:
        return
    from app.db.session import SessionLocal
    from app.services.loader import upsert_startups

    with SessionLocal() as session:
        count = upsert_startups(session, data)
    print(f"✅ Saved {count} startups to PostgreSQL")


def main():
    driver = init_driver()
    data = []
    
    # You can modify this URL to scrape different categories
    url = "https://startups.gallery/categories/stages/series-c"
    
    try:
        print("Starting scraper...")
        print("This will scroll through the page to load all companies")
        print("Press Ctrl+C to stop if needed\n")
        
        data = scrape_investors(driver, url)
        
        if data:
            save_csv(data)
            save_to_db(data)
            print("\n" + "="*80)
            print(f"🎉 COMPLETE! Scraped {len(data)} companies successfully!")
            print("="*80)
        else:
            print("\n⚠️  No data was scraped.")
            print("Check the page_source.html file in your Downloads folder to see the actual HTML.")
            print("You may need to adjust the CSS selectors based on the real page structure.")
        
        time.sleep(3)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
        if data:
            print(f"Saving {len(data)} companies collected so far...")
            save_csv(data)
            save_to_db(data)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        if data:
            print(f"Saving {len(data)} companies collected before error...")
            save_csv(data)
            save_to_db(data)
    finally:
        driver.quit()
        print("Browser closed.")

if __name__ == "__main__":
    main()