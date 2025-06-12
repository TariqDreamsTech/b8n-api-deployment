import requests
from bs4 import BeautifulSoup
import json
import time

# Target URL
url = "https://www.elmoraautosales2.com/cars-for-sale"

# Headers
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "cookie": 'hammer-chat={"minimized":true,"lastOpenedTimestamp":0,"uuid":"8ad46620-fbbf-4e8b-830e-6cdbaafd3324"}; _gid=GA1.2.1563192244.1749664298; _ga_6P5L4GZ20D=GS2.1.s1749664297$o1$g1$t1749664931$j59$l0$h0; _ga=GA1.1.2115226872.1749664298; _ga_LH5WKR0S86=GS2.2.s1749664353$o1$g1$t1749664935$j60$l0$h0; datadome=ZOGxBJVBE8vy3A9U~Bb5DgQQL_U0b14Bdco0nCrLFwtIAhgExbFBkCA4KEdExVxmUKsqQXSsJRBn7veWNMt_uq~epWMX8bWoDG3KGKRya43CSB5u6Ai9Hxna6~KhPhfi',
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
}


def get_inventory_list():
    """
    Fetch all pages of results and return the complete inventory list
    """
    try:
        all_vehicle_data = []
        page_number = 1

        while True:
            print(f"Scraping page {page_number}...")
            params = {
                "PageNumber": str(page_number),
                "Sort": "MakeAsc",
                "StockNumber": "",
                "Condition": "",
                "BodyStyle": "",
                "Make": "",
                "MaxPrice": "",
                "Mileage": "",
                "SoldStatus": "AllVehicles",
            }

            response = requests.get(url, headers=headers, params=params)
            soup = BeautifulSoup(response.text, "html.parser")
            json_ld_scripts = soup.find_all("script", type="application/ld+json")

            found_vehicle = False
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get("@type") == "Vehicle":
                        all_vehicle_data.append(data)
                        found_vehicle = True
                    elif isinstance(data, list):
                        for item in data:
                            if (
                                isinstance(item, dict)
                                and item.get("@type") == "Vehicle"
                            ):
                                all_vehicle_data.append(item)
                                found_vehicle = True
                except Exception as e:
                    print(f"Error parsing script: {e}")

            # Stop if no vehicle found on this page
            if not found_vehicle:
                print(f"No vehicles found on page {page_number}. Stopping.")
                break

            # Check if a "Next" page exists by looking for a pagination link
            next_button = soup.select_one(
                'a.data-button-next-page[data-trackingid="search-pagination-next"]'
            )
            if not next_button:
                print("No 'Next' button found. Scraping complete.")
                break

            page_number += 1
            time.sleep(1)  # polite delay

        print(f"\nTotal vehicles scraped: {len(all_vehicle_data)}")
        return all_vehicle_data
    except Exception as e:
        print(f"Error getting inventory list: {str(e)}")
        return []
