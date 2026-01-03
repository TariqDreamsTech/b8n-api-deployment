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
    """
    while True:
        print(f"Requesting {target_url}...")
        
        # simplified params matching the curl
        sa_params = {
            "url": target_url,
            "x-api-key": SA_API_KEY,
            "proxy_type": "residential"
        }

        try:
            response = requests.get(SA_URL, params=sa_params, timeout=60)
            
            if response.status_code == 200:
                if "Access Denied" in response.text:
                     print(f"Access Denied. Retrying...")
                     time.sleep(1)
                     continue
                return response.text
            elif response.status_code == 423:
                print("Status 423 (Locked). This usually means the resource is blocked or requires better proxy/headers.")
                print("Retrying in 2s...")
                time.sleep(2)
            elif response.status_code == 429:
                print("Rate limit reached. Waiting 5s...")
                time.sleep(5)
            else:
                print(f"Status {response.status_code}. Retrying...")
                time.sleep(1)
                
        except Exception as e:
            print(f"Error: {e}. Retrying...")
            time.sleep(1)

def get_inventory_list():
    all_vehicle_data = []

    # Iterate through 9 pages as requested
    for page_number in range(1, 10):
        print(f"\nScraping page {page_number}...")
        
        target_url = f"https://www.m2mcars.com/inventory?perpage=24&page_no={page_number}"
        
        html = get_page_html(target_url)
        soup = BeautifulSoup(html, "html.parser")
        
        vehicles_found = 0
        
        inventory_items = soup.select("div.vehicle-container")
        
        for item in inventory_items:
            # ---- VIN ----
            vin_data = item.get("data-vehicle-id")
            vin = vin_data.replace("vehicle-id-", "") if vin_data else None

            # ---- TITLE & URL ----
            title_tag = item.select_one("a.vehicle-title")
            title = title_tag.get_text(strip=True) if title_tag else None
            vehicle_url = title_tag.get("href") if title_tag else None
            if vehicle_url and not vehicle_url.startswith("http"):
                vehicle_url = "https://www.m2mcars.com" + vehicle_url

            # ---- PRICE ----
            price_tag = item.select_one(".vehicle-price-value")
            price = price_tag.get_text(strip=True) if price_tag else None

            # ---- STOCK NUMBER ----
            stock_tag = item.select_one(".vehicle-field-stocknumber .vehicle-info-value")
            stock_no = stock_tag.get_text(strip=True) if stock_tag else None

            # ---- MILEAGE ----
            mileage_tag = item.select_one(".vehicle-field-odometer .vehicle-info-value")
            mileage = mileage_tag.get_text(strip=True) if mileage_tag else None

            # ---- DRIVETRAIN ----
            drivetrain_tag = item.select_one(".vehicle-field-drivetrain .vehicle-info-value")
            drivetrain = drivetrain_tag.get_text(strip=True) if drivetrain_tag else None
            
            # ---- IMAGE ----
            img_tag = item.select_one("img.vehicle-image")
            image_url = img_tag.get("src") if img_tag else None

            # ---- YEAR / MAKE / MODEL Parsing ----
            year = make = model = None
            if title:
                parts = title.split()
                if len(parts) >= 2 and parts[0].isdigit():
                    year = parts[0]
                    make = parts[1]
                    model = " ".join(parts[2:])

            
            vehicle_data = {
                "title": title,
                "year": year,
                "make": make,
                "model": model,
                "price": price,
                "stock_no": stock_no,
                "vin": vin,
                "mileage": mileage,
                "drivetrain": drivetrain,
                "image_url": image_url,
                "vehicle_url": vehicle_url
            }
            
            all_vehicle_data.append(vehicle_data)
            vehicles_found += 1
            
        print(f"Found {vehicles_found} vehicles on page {page_number}")
        time.sleep(1)

    print(json.dumps(all_vehicle_data, indent=4))
    return all_vehicle_data

if __name__ == "__main__":
    get_inventory_list()
