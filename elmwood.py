import requests
from bs4 import BeautifulSoup
import json
import time

# ScrapingAnt API Config
SA_API_KEY = "c615fc4e6f78408586991e5e90069dd5"
SA_URL = "https://api.scrapingant.com/v2/general"
BASE_URL = "https://www.elmwoodautosalesri.com"

def get_page_html(target_url):
    """
    Fetches the page content using ScrapingAnt.
    """
    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        print(f"Requesting {target_url}...")
        
        sa_params = {
            "url": target_url,
            "x-api-key": SA_API_KEY,
            "proxy_type": "residential",
            "browser": "false" 
        }

        try:
            response = requests.get(SA_URL, params=sa_params, timeout=60)
            
            if response.status_code == 200:
                if "Access Denied" in response.text:
                     print(f"Access Denied content detected. Retrying...")
                     time.sleep(2)
                     retry_count += 1
                     continue
                return response.text
            elif response.status_code == 429:
                print("Rate limit reached. Waiting 5s...")
                time.sleep(5)
            else:
                print(f"Status {response.status_code}. Retrying...")
                time.sleep(2)
                retry_count += 1
                
        except Exception as e:
            print(f"Error: {e}. Retrying...")
            time.sleep(2)
            retry_count += 1
            
    print(f"Failed to fetch {target_url} after {max_retries} retries.")
    return None

def get_inventory_list():
    all_vehicle_data = []

    # Iterate through 2 pages as requested
    for page_number in range(1, 3):
        page_retries = 0
        max_page_retries = 5
        
        while page_retries < max_page_retries:
            print(f"\nScraping page {page_number} (Attempt {page_retries + 1})...")
            
            target_url = f"https://www.elmwoodautosalesri.com/inventory/?perpage=100&page_no={page_number}"
            
            html = get_page_html(target_url)
            if not html:
                page_retries += 1
                time.sleep(2)
                continue
                
            soup = BeautifulSoup(html, "html.parser")
            
            vehicles = soup.find_all("div", class_="vehicle-container")
            if not vehicles:
                print(f"Found 0 vehicles on page {page_number}. Retrying...")
                page_retries += 1
                time.sleep(3)
                continue
                
            vehicles_found = 0
            
            for vehicle in vehicles:
                try:
                    # ---- VIN ----
                    vin_id = vehicle.get("data-vehicle-id", "")
                    vin = vin_id.replace("vehicle-id-", "") if vin_id else None
                    
                    # ---- TITLE & URL ----
                    title_tag = vehicle.find("a", class_="vehicle-title")
                    title = title_tag.get_text(strip=True) if title_tag else "Unknown"
                    href = title_tag["href"] if title_tag else ""
                    if href and not href.startswith("http"):
                         href = BASE_URL + href
                    
                    # ---- PRICE ----
                    price_tag = vehicle.find("span", class_="vehicle-price-value")
                    price = price_tag.get_text(strip=True) if price_tag else None
                    
                    # ---- IMAGE ----
                    img_tag = vehicle.find("img", class_="vehicle-image")
                    img_url = None
                    if img_tag:
                        # Prefer srcset if available, taking the largest or first
                        srcset = img_tag.get("srcset")
                        if srcset:
                            # Extract first url from srcset
                            img_url = srcset.split(",")[0].split(" ")[0]
                        else:
                            img_url = img_tag.get("src")
                    
                    # ---- SPECS ----
                    def get_spec(field_class):
                        # Finds the value span inside a container with specific class
                        # Only expects one value, so finds first occurrence (handles duplicate mobile/desktop blocks)
                        container = vehicle.find("div", class_=field_class)
                        if container:
                            val = container.find("span", class_="vehicle-info-value")
                            if val:
                                 return val.get_text(strip=True)
                        return None

                    stock = get_spec("vehicle-field-stocknumber")
                    fuel = get_spec("vehicle-field-fueltype")
                    drivetrain = get_spec("vehicle-field-drivetrain")
                    color = get_spec("vehicle-field-exteriorcolor")
                    transmission = get_spec("vehicle-field-transmission")
                   
                    vehicle_data = {
                        "title": title,
                        "url": href,
                        "image": img_url,
                        "price": price,
                        "vin": vin,
                        "stock": stock,
                        "fuel": fuel,
                        "drivetrain": drivetrain,
                        "exterior_color": color,
                        "transmission": transmission
                    }
                    
                    all_vehicle_data.append(vehicle_data)
                    vehicles_found += 1
                    
                except Exception as e:
                    print(f"Error parsing vehicle: {e}")
                    continue

            print(f"Found {vehicles_found} vehicles on page {page_number}")
            time.sleep(1)
            break # Exit retry loop as we found vehicles

    # Output total scraped vehicles as single JSON
    print(json.dumps(all_vehicle_data, indent=4))
    return all_vehicle_data

if __name__ == "__main__":
    get_inventory_list()
