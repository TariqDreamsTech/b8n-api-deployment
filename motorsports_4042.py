import math
import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://www.4042motorsports.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "Referer": BASE_URL + "/inventory/used-cars-willow-springs-nc",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
PROXIES = {
    "http": "http://henrywoowgraphics:udFdNect4I@89.116.56.101:50100",
    "https": "http://henrywoowgraphics:udFdNect4I@89.116.56.101:50100",
}


def get_total_pages():
    """Get total vehicle count and number of pages"""
    url = BASE_URL + "/inventory/used-cars-willow-springs-nc?page=0&npp=25&st=loc:1695"
    response = requests.get(url, headers=HEADERS, proxies=PROXIES)
    soup = BeautifulSoup(response.text, "lxml")

    count_tag = soup.select_one("h4.browse-result-count")
    if count_tag:
        total = int(count_tag.text.strip())
        pages = math.ceil(total / 25)
        return total, pages
    return 0, 0


def parse_vehicle_data(soup):
    """Parse vehicle data from a single page"""
    listings = []
    containers = soup.select(".listing-data-container")

    for container in containers:
        title = container.select_one("h3#srp-title")
        link = container.select_one("a#srp-title")
        img = container.select_one("img.srp-image")
        price = container.select_one("text.p1price")
        mileage = container.select_one("text#mileage")
        engine = container.select_one("text#engine")
        bodystyle = container.select_one("text#bodystyle")
        color = container.select_one("text#color")

        listings.append(
            {
                "Title": title.text.strip() if title else "",
                "Link": (
                    BASE_URL + link["href"] if link and link.has_attr("href") else ""
                ),
                "Image": img["src"] if img and img.has_attr("src") else "",
                "Price": price.text.strip() if price else "",
                "Mileage": mileage.text.strip() if mileage else "",
                "Engine": engine.text.strip() if engine else "",
                "Body Style": bodystyle.text.strip() if bodystyle else "",
                "Color": color.text.strip() if color else "",
            }
        )
    return listings


def get_inventory_list():
    """Get all inventory from all pages"""
    total, pages = get_total_pages()
    print(f"Total Vehicles: {total} | Pages: {pages}")
    all_listings = []

    for page in range(0, pages):
        print(f"Scraping Page {page + 1}/{pages}")
        url = f"{BASE_URL}/inventory/used-cars-willow-springs-nc?page={page}&npp=25&st=loc:1695"
        response = requests.get(url, headers=HEADERS, proxies=PROXIES)
        soup = BeautifulSoup(response.text, "lxml")
        listings = parse_vehicle_data(soup)
        all_listings.extend(listings)

    return all_listings


if __name__ == "__main__":
    data = get_inventory_list()
    print(len(data))
    print(json.dumps(data, indent=2))
