import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import re

PROXIES = {
    "http": "http://henrywoowgraphics:udFdNect4I@185.240.121.143:50100",
    "https": "http://henrywoowgraphics:udFdNect4I@185.240.121.143:50100",
}


def get_inventory_list():
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}

    base_url = "https://www.pujolsautosale.com/inventory/?page_no="
    json_urls = []

    # Step 1: Get JSON endpoints from all pages
    for page in range(1, 7):
        url = base_url + str(page)
        try:
            response = requests.get(url, headers=headers, timeout=10, proxies=PROXIES)
            soup = BeautifulSoup(response.text, "html.parser")
            for script in soup.find_all("script", src=True):
                if "/inv-scripts-v2/inv/vehicles" in script["src"]:
                    full_url = urljoin(url, script["src"])
                    json_urls.append(full_url)
                    break
        except Exception as e:
            print(f"Error fetching page {page}:", e)

    # Step 2: Fetch vehicle data from each JSON URL
    all_vehicles = []

    for i, json_url in enumerate(json_urls, 1):
        print(f"\n[Fetching JSON Page {i}] {json_url}")
        try:
            res = requests.get(json_url, headers=headers, timeout=10, proxies=PROXIES)
            match = re.search(r"dws_inventory_listing_4\((\{.*\})\)", res.text)
            if match:
                data = json.loads(match.group(1))
                vehicles = data.get("Vehicles", [])
                for v in vehicles:
                    make = v.get("Make", "").lower().replace(" ", "-")
                    model = v.get("Model", "").lower().replace(" ", "-")
                    stock = v.get("StockNumber", "").strip()
                    detail_url = f"https://www.pujolsautosale.com/inventory/{make}/{model}/{stock}/"
                    v["DetailURL"] = detail_url
                all_vehicles.extend(vehicles)
                print(f"Added {len(vehicles)} vehicles from page {i}")
            else:
                print("No JSON match.")
        except Exception as e:
            print("Error fetching JSON:", e)

    return all_vehicles


if __name__ == "__main__":
    vehicles = get_inventory_list()
    print("\n--- Vehicles Summary ---")
    for v in vehicles:
        year = v.get("Year", "N/A")
        model = v.get("Model", "N/A")
        price = v.get("VehiclePrice", "N/A")
        url = v.get("DetailURL", "N/A")
        print(f"{year} {model} | Price: ${price} | URL: {url}")
