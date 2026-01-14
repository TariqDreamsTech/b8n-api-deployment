import requests
from bs4 import BeautifulSoup
import json
import time
import random
import urllib.parse

# Algolia API Config
ALGOLIA_URL = 'https://g58lko3etj-dsn.algolia.net/1/indexes/production-inventory-global_price_desc/query?x-algolia-agent=Algolia%20for%20JavaScript%20(4.18.0)%3B%20Browser%20(lite)&x-algolia-api-key=cc3dce06acb2d9fc715bc10c9a624d80&x-algolia-application-id=G58LKO3ETJ'

def get_inventory_list():
    base_url = "https://jandsautohaus6.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0',
        'Accept': '*/*',
        'content-type': 'application/x-www-form-urlencoded',
        'Origin': 'https://jandsautohaus6.com',
        'Referer': 'https://jandsautohaus6.com/',
    }

    data = {
        "query": "",
        "clickAnalytics": True,
        "userToken": "3LlBvoxUyXqI",
        "filters": "functional_price >= 0 AND functional_price <= 45000 AND is_active:true AND dealer_ids:\"662\" AND dealer_id:662<score=1> OR dealer_id:659<score=0> OR dealer_id:660<score=0> OR dealer_id:661<score=0>",
        "optionalFilters": [],
        "offset": 0,
        "length": 500 
    }

    try:
        response = requests.post(ALGOLIA_URL, headers=headers, data=json.dumps(data), timeout=60)
        if response.status_code != 200:
            return []

        results = response.json()
        hits = results.get('hits', [])

        final_results = []
        for hit in hits:
            # Constructing data based on observed Algolia schema
            # Use 'or' to handle cases where key exists but value is null
            make = hit.get('make') or ''
            model = hit.get('model') or ''
            year = hit.get('make_year') or ''
            trim = hit.get('car_trim') or ''
            
            # Clean up N/A or empty trim
            trim_str = f" {trim}" if trim else ""
            vehicle_name = f"{year} {make} {model}{trim_str}".strip()
            
            transmission = hit.get('transmission') or 'N/A'
            price = hit.get('functional_price') or 'N/A'
            vin = hit.get('vin') or ''
            condition = hit.get('car_condition') or 'Used'
            
            # Construct Link
            slug_make = str(make).replace(" ", "_")
            slug_model = str(model).replace(" ", "_")
            slug_trim = str(trim).replace(" ", "_") if trim else ""
            trim_part = f"-{slug_trim}" if slug_trim else ""
            
            vehicle_url = f"{base_url}/inventory/{condition}-{year}-{slug_make}-{slug_model}{trim_part}-{vin}"
            
            # All Images
            image_ids = hit.get('images') or []
            all_images = [f"https://images.app.ridemotive.com/{img_id}" for img_id in image_ids]

            vehicle_data = {
                "Vehicle Name": vehicle_name,
                "Gear / Transmission": transmission,
                "Vehicle Link": vehicle_url,
                "Total Price": f"${price}" if price != 'N/A' else 'N/A',
                "Images": all_images
            }
            final_results.append(vehicle_data)

        return final_results

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

if __name__ == "__main__":
    inventory = get_inventory_list()
    print(f"Found {len(inventory)} vehicles.")
    if inventory:
        print(json.dumps(inventory[0], indent=4))
