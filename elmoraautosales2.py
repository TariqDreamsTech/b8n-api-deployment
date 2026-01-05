import requests
from bs4 import BeautifulSoup
import json
import time
import random

# ScrapingAnt API Config
SA_API_KEY = "c615fc4e6f78408586991e5e90069dd5"
SA_URL = "https://api.scrapingant.com/v2/general"


def get_page_html(target_url):
    """
    Fetches the page content using ScrapingAnt.
    Rotates proxy country if browser is detected or request fails.
    """
    while True:
        
        sa_params = {
            "url": target_url,
            "x-api-key": SA_API_KEY,
            "proxy_type": "residential", # Using residential as base
            "browser": "true"
        }

        try:
            response = requests.get(SA_URL, params=sa_params, timeout=60)
            
            # Check for browser detection message in response
            if "browser was detected" in response.text:
                print(f"Browser detected with. Rotating proxy...")
                continue
                
            if response.status_code == 200:
                return response.text
            else:
                print(f"Status {response.status_code}. Retrying...")
                
        except Exception as e:
            print(f"Error: {e}. Retrying...")
        
        time.sleep(1)

def get_inventory_list():
    all_vehicle_data = []

    # Iterate through 3 pages as requested
    # Iterate through 3 pages as requested
    for page_number in range(1, 4):
        page_retries = 0
        max_page_retries = 5
        
        while page_retries < max_page_retries:
            print(f"\nScraping page {page_number} (Attempt {page_retries + 1})...")
            
            target_url = f"https://www.elmoraautosales2.com/cars-for-sale?PageNumber={page_number}&Sort=MakeAsc&SoldStatus=AllVehicles"
            
            html = get_page_html(target_url)
            if not html: # Assuming get_page_html returns string or raises exception. But wait, in elmoraautosales2.py it loops internally or retries?
                         # The provided elmoraautosales2.py doesn't return None on failure in get_page_html, it loops endlessly.
                         # But let's assume it returns text.
                pass
            
            soup = BeautifulSoup(html, "html.parser")
            
            # Use select like before
            vehicles = soup.select(".vehicle-snapshot")
            
            if not vehicles:
                print(f"Found 0 vehicles on page {page_number}. Retrying...")
                page_retries += 1
                time.sleep(3)
                continue

            vehicles_found = 0
            for card in vehicles:
                # ---- TITLE ----
                title_tag = card.select_one(".vehicle-snapshot__title a")
                title = title_tag.get_text(strip=True) if title_tag else None
                vehicle_url = (
                    "https://www.elmoraautosales2.com" + title_tag["href"]
                    if title_tag else None
                )

                # ---- YEAR / MAKE / MODEL ----
                year = make = model = None
                if title:
                    parts = title.split()
                    if parts[0].isdigit():
                        year = parts[0]
                        make = parts[1]
                        model = " ".join(parts[2:])

                # ---- DESCRIPTION ----
                desc = card.select_one(".vehicle-snapshot__style")
                description = desc.get_text(strip=True) if desc else None

                # ---- IMAGE ----
                img = card.select_one(".vehicle-snapshot__image img")
                image_url = None
                has_image = False

                if img:
                    src = img.get("src")
                    fallback = img.get("data-fallback-img-src")
                    if src and "cdn09.carsforsale.com/images/nophoto" not in src:
                        image_url = src
                        has_image = True
                    else:
                        image_url = fallback
                        has_image = False
                
                # ---- PRICE ----
                price_tag = card.select_one(".vehicle-snapshot__main-info.font-primary")
                price = price_tag.get_text(strip=True) if price_tag else None
                
                vehicle_data = {
                    "year": year,
                    "make": make,
                    "model": model,
                    "description": description,
                    "url": vehicle_url,
                    "image_url": image_url,
                    "has_image": has_image,
                    "price": price
                }
                all_vehicle_data.append(vehicle_data)
                vehicles_found += 1
                
            print(f"Found {vehicles_found} vehicles on page {page_number}")
            time.sleep(1)
            break # Exit retry loop

    # Output total scraped vehicles as single JSON
    print(json.dumps(all_vehicle_data, indent=4))
    return all_vehicle_data

if __name__ == "__main__":
    get_inventory_list()
