import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import math
import time

BASE_URL = "https://www.northwestindianaautofinance.com/inventory"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0"
}

proxies = {
    "http": "http://henrywoowgraphics:udFdNect4I@185.240.121.143:50100",
    "https": "http://henrywoowgraphics:udFdNect4I@185.240.121.143:50100",
}


def safe_request(url, retries=3, timeout=15):
    for i in range(retries):
        try:
            return requests.get(url, headers=HEADERS, proxies=proxies, timeout=timeout)
        except Exception as e:
            print(f"Retry {i+1}/{retries} for {url}: {e}")
            time.sleep(2)
    return None


def parse_vehicle(div, base_url):
    title_tag = div.select_one("h4.i08r_vehicleTitleGrid a")
    title = title_tag.get_text(strip=True) if title_tag else "N/A"
    link = urljoin(base_url, title_tag["href"]) if title_tag else "N/A"

    img_tag = div.select_one(".i08r_image img")
    image_url = img_tag["src"] if img_tag else "N/A"

    def get_field(class_name):
        p = div.select_one(f"p.{class_name}")
        return p.get_text(strip=True).split(":", 1)[-1].strip() if p else "N/A"

    stock = get_field("i08r_optStock")
    engine = get_field("i08r_optEngine")
    transmission = get_field("i08r_optTrans")
    drive = get_field("i08r_optDrive")
    mileage = get_field("i08r_optMileage")
    color = get_field("i08r_optColor")
    vin = get_field("i08r_optVin")

    price_tag = div.select_one(".price-2")
    price = price_tag.get_text(strip=True) if price_tag else "N/A"

    return {
        "Title": title,
        "Link": link,
        "Image URL": image_url,
        "Stock": stock,
        "Engine": engine,
        "Transmission": transmission,
        "Drive": drive,
        "Mileage": mileage,
        "Color": color,
        "VIN": vin,
        "Price": price,
    }


def scrape_page(page_num):
    url = BASE_URL if page_num == 1 else f"{BASE_URL}?page={page_num}"
    print(f"Scraping page: {url}")
    res = safe_request(url)
    if res and res.ok:
        soup = BeautifulSoup(res.text, "html.parser")
        vehicles = soup.select(".i08r-invBox")
        return [parse_vehicle(v, BASE_URL) for v in vehicles]
    else:
        print(f"Failed to get page {page_num}")
        return []


def get_total_pages():
    res = safe_request(BASE_URL)
    if res and res.ok:
        soup = BeautifulSoup(res.text, "html.parser")
        pager_summary = soup.select_one(".pager-summary")
        total_vehicles = 0
        if pager_summary:
            text = pager_summary.get_text(strip=True)
            match = re.search(r"\((\d+)\s+vehicles\)", text)
            if match:
                total_vehicles = int(match.group(1))
        per_page = 48
        total_pages = math.ceil(total_vehicles / per_page) if total_vehicles else 1
        return total_pages
    return 1


def get_inventory_count():
    res = safe_request(BASE_URL)
    if res and res.ok:
        soup = BeautifulSoup(res.text, "html.parser")
        pager_summary = soup.select_one(".pager-summary")
        if pager_summary:
            text = pager_summary.get_text(strip=True)
            match = re.search(r"\((\d+)\s+vehicles\)", text)
            if match:
                return int(match.group(1))
    return 0


def get_inventory_list():
    total_pages = get_total_pages()
    print(f"Total pages to scrape: {total_pages}")

    all_vehicles = []
    for page in range(1, total_pages + 1):
        all_vehicles.extend(scrape_page(page))

    print(f"Total vehicles scraped: {len(all_vehicles)}")
    return all_vehicles


def run_scraper():
    vehicles_data = get_inventory_list()
    print(f"Scraped {len(vehicles_data)} vehicles")
    return vehicles_data
