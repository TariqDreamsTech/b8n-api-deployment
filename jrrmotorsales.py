import requests
from bs4 import BeautifulSoup
import json
import time

# ScrapingAnt API Config
SA_API_KEY = "c615fc4e6f78408586991e5e90069dd5"
SA_URL = "https://api.scrapingant.com/v2/general"
BASE_URL = "https://www.jrrmotorsales.com"

def get_page_html(target_url):
    """
    Fetches the page content using ScrapingAnt.
    """
    retry_count = 0
    max_retries = 10
    
    while retry_count < max_retries:
        print(f"Requesting {target_url}...")
        
        sa_params = {
            "url": target_url,
            "x-api-key": SA_API_KEY,
            "proxy_type": "residential",
            "browser": "true"  # Try without browser first as it might be faster/cheaper, or match curl
        }

        try:
            # Using the curl command as reference, it's a simple GET
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
                # Don't increment retry count for rate limits, just wait
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
            
            # URL from user request: https://www.jrrmotorsales.com/inventory?page=1&pageSize=100
            target_url = f"{BASE_URL}/inventory?page={page_number}&pageSize=100"
            
            html = get_page_html(target_url)
            if not html:
                page_retries += 1
                time.sleep(2)
                continue
                
            soup = BeautifulSoup(html, "html.parser")
            
            vehicles = soup.find_all("div", class_="invMainCell")
            if not vehicles:
                print(f"Found 0 vehicles on page {page_number}. Retrying...")
                page_retries += 1
                time.sleep(3)
                continue
                
            vehicles_found = 0
            
            for vehicle in vehicles:
                try:
                    # ---- IMAGE ----
                    img_div = vehicle.find("div", class_="i10r_image")
                    img_tag = img_div.find("img") if img_div else None
                    img_url = ""
                    if img_tag:
                        img_url = img_tag.get("data-src") or img_tag.get("src")
                    
                    # ---- TITLE & LINK ----
                    info_div = vehicle.find("div", class_="i10r_mainWrap")
                    title_tag = info_div.find("h4", class_="i10r_vehicleTitle").find("a") if info_div else None
                    
                    title = title_tag.get_text(strip=True) if title_tag else "Unknown"
                    href = title_tag["href"] if title_tag else ""
                    full_link = f"{BASE_URL}{href}" if href and not href.startswith("http") else href

                    # ---- FEATURES ----
                    # Helper to extract text from labels
                    def get_feature(parent, cls_name):
                        el = parent.find("p", class_=cls_name)
                        if el:
                            # Text could be "Label: Value", strip the label (e.g. "Color:")
                            text = el.get_text(strip=True)
                            if ":" in text:
                                return text.split(":", 1)[1].strip()
                            return text
                        return None

                    if info_div:
                        color = get_feature(info_div, "i10r_optColor")
                        interior = get_feature(info_div, "i10r_optInterior")
                        drive = get_feature(info_div, "i10r_optDrive")
                        trans = get_feature(info_div, "i10r_optTrans")
                        vin = get_feature(info_div, "i10r_optVin")
                        engine = get_feature(info_div, "i10r_optEngine")
                        mileage = get_feature(info_div, "i10r_optMileage")
                        stock = get_feature(info_div, "i10r_optStock")
                        
                        # ---- PRICE ----
                        price_tag = info_div.find("span", class_="price-2")
                        price = price_tag.get_text(strip=True) if price_tag else None
                    else:
                        color = interior = drive = trans = vin = engine = mileage = stock = price = None

                    vehicle_data = {
                        "title": title,
                        "url": full_link,
                        "image": img_url,
                        "price": price,
                        "mileage": mileage,
                        "stock": stock,
                        "vin": vin,
                        "engine": engine,
                        "transmission": trans,
                        "drivetrain": drive,
                        "exterior_color": color,
                        "interior_color": interior
                    }
                    
                    all_vehicle_data.append(vehicle_data)
                    vehicles_found += 1
                    
                except Exception as e:
                    print(f"Error parsing vehicle: {e}")
                    continue

            print(f"Found {vehicles_found} vehicles on page {page_number}")
            time.sleep(1)
            break # Exit retry loop

    # Output total scraped vehicles as single JSON
    print(json.dumps(all_vehicle_data, indent=4))
    return all_vehicle_data

if __name__ == "__main__":
    get_inventory_list()
