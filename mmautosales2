import requests
from bs4 import BeautifulSoup
import json
import time
import random

# ScrapingAnt API Config
SA_API_KEY = "c615fc4e6f78408586991e5e90069dd5"
SA_URL = "https://api.scrapingant.com/v2/general"

# List of available proxy countries
PROXY_COUNTRIES = [
    "US"
]

def get_page_html(target_url):
    """
    Fetches the page content using ScrapingAnt.
    Rotates proxy country if browser is detected or request fails.
    """
    retries = 0
    max_retries = 5
    
    while retries < max_retries:
        # Pick a random country
        country = random.choice(PROXY_COUNTRIES)
        print(f"Trying with proxy country: {country}...")
        
        sa_params = {
            "url": target_url,
            "x-api-key": SA_API_KEY,
            "proxy_country": country,
            "proxy_type": "residential",
            "browser": True
        }

        try:
            response = requests.get(SA_URL, params=sa_params, timeout=60)
            
            # Check for browser detection message in response
            if "browser was detected" in response.text:
                print(f"Browser detected with {country}. Rotating proxy...")
                retries += 1
                continue
                
            if response.status_code == 200:
                print("Successfully fetched page.")
                return response.text
            else:
                print(f"Status {response.status_code}. Retrying...")
                retries += 1
                
        except Exception as e:
            print(f"Error: {e}. Retrying...")
            retries += 1
        
        time.sleep(2)  # Wait a bit before retry
    
    print("Max retries reached. Could not get page.")
    return None

def get_inventory_list():
    all_vehicle_data = []

    # Iterate through pages. The user URL had Page=1, PageSize=400.
    # We will try page 1. The loop logic is good if there are multiple pages,
    # but 400 items fits on one page usually for these sites. 
    # Let's assume there might be more if the inventory is huge, but start with 1.
    # The user specifically asked for "scrape make year model vehicle url and image url".
    
    page_number = 1
    has_next_page = True
    
    while has_next_page:
        print(f"\nScraping page {page_number}...")
        
        target_url = f"https://www.mmautosales2.com/inventory?clearall=1&Page={page_number}&PageSize=400"
        
        html = get_page_html(target_url)
        if not html:
            break
        
        soup = BeautifulSoup(html, "html.parser")
        
        # Check if there are vehicles
        # Based on user snippet: <div class=" i17r-vehicle-body row">
        vehicles = soup.select("div.i17r-vehicle-body.row")
        
        if not vehicles:
            print(f"Found 0 vehicles on page {page_number}. Stopping.")
            break

        vehicles_found = 0
        for card in vehicles:
            # ---- YEAR / MAKE / MODEL / URL ----
            # <h4 class="vehicleTitleH4">
            #    <a aria-label="2012 Buick Enclave Leather FWD" href="/vdp/..."> 2012 Buick Enclave </a>
            # </h4>
            title_link = card.select_one("h4.vehicleTitleH4 a")
            
            full_title = title_link.get_text(strip=True) if title_link else None
            vehicle_url = None
            if title_link and title_link.get("href"):
                vehicle_url = "https://www.mmautosales2.com" + title_link.get("href")
            
            year = make = model = None
            if full_title:
                parts = full_title.split()
                if len(parts) >= 2 and parts[0].isdigit():
                    year = parts[0]
                    make = parts[1]
                    model = " ".join(parts[2:])
            
            # ---- IMAGE URL ----
            # <div class="mainImgWrap col-lg-3">
            #   <a class="i17_vehicleTitle" ...>
            #     <img src="..." ... class="img-fluid i17r_mainImg " ...>
            #   </a>
            img_tag = card.select_one(".mainImgWrap img.i17r_mainImg")
            image_url = None
            if img_tag:
                 image_url = img_tag.get("src")
                 # Handle fallback or empty src if needed? usually src is good here.
            
            
            if full_title: # Only add if we got a title at least
                vehicle_data = {
                    "year": year,
                    "make": make,
                    "model": model,
                    "vehicle_url": vehicle_url,
                    "image_url": image_url
                }
                all_vehicle_data.append(vehicle_data)
                vehicles_found += 1
                
        print(f"Found {vehicles_found} vehicles on page {page_number}")
        
        # If we found fewer than 400, it's likely the last page.
        # But also, if `vehicles_found` is 0, we broke above.
        if vehicles_found < 400:
             has_next_page = False
        else:
             page_number += 1
             time.sleep(1)

    # Output total scraped vehicles as single JSON
    output_json = json.dumps(all_vehicle_data, indent=4)
    print(output_json)
    

if __name__ == "__main__":
    get_inventory_list()
