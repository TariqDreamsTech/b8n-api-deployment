import requests
from bs4 import BeautifulSoup
import time

url = "https://www.massmotors.com/cars-for-sale?PageSize=150"

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
    "referer": "https://www.massmotors.com/cars-for-sale",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
}


def safe_request(url, retries=3, timeout=15):
    for i in range(retries):
        try:
            return requests.get(url, headers=headers, timeout=timeout)
        except Exception as e:
            print(f"Retry {i+1}/{retries} for {url}: {e}")
            time.sleep(2)
    return None


def get_inventory_count():
    response = safe_request(url)
    if response and response.ok:
        soup = BeautifulSoup(response.text, "html.parser")
        result_span = soup.find(
            "span", class_="inventory-header-filters__results-count"
        )
        if result_span:
            counts = result_span.find_all("span", class_="font-weight-600")
            if len(counts) >= 3:
                total_vehicles = int(counts[-1].text.strip())
                return total_vehicles
    return 0


def extract_vehicle_data(vehicle):
    def safe_select_text(selector):
        el = vehicle.select_one(selector)
        return el.get_text(strip=True) if el else ""

    def safe_img_src(selector):
        img = vehicle.select_one(selector)
        return img["src"] if img and "src" in img.attrs else ""

    def safe_href(selector):
        a = vehicle.select_one(selector)
        return (
            "https://www.massmotors.com" + a["href"] if a and "href" in a.attrs else ""
        )

    return {
        "title": safe_select_text(".vehicle-snapshot__title a"),
        "link": safe_href(".vehicle-snapshot__title a"),
        "image_url": safe_img_src(".vehicle-snapshot__image img"),
        "price": safe_select_text(
            ".vehicle-snapshot__main-info-item:nth-of-type(1) .vehicle-snapshot__main-info"
        ),
        "mileage": safe_select_text(
            ".vehicle-snapshot__main-info-item:nth-of-type(2) .vehicle-snapshot__main-info"
        ),
    }


def get_inventory_list():
    response = safe_request(url)
    if response and response.ok:
        soup = BeautifulSoup(response.text, "html.parser")
        vehicles = soup.select("li.vehicle-snapshot")
        all_data = [extract_vehicle_data(vehicle) for vehicle in vehicles[1:]]
        print(f"Total vehicles scraped: {len(all_data)}")
        return all_data
    else:
        print("Failed to get inventory data")
        return []


def run_scraper():
    vehicles_data = get_inventory_list()
    print(f"Scraped {len(vehicles_data)} vehicles")
    return vehicles_data
