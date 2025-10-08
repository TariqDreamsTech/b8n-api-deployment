import requests
from bs4 import BeautifulSoup
import math
import time

# Base URL and settings
base_url = "https://www.savvyautosale.com"
start_url = base_url + "/used-cars-in-columbus-oh/page/1"

# Headers and proxy settings
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}

PROXIES = {
    "http": "http://henrywoowgraphics:udFdNect4I@89.116.56.101:50100",
    "https": "http://henrywoowgraphics:udFdNect4I@89.116.56.101:50100",
}


def get_total_count():
    """
    Get the total number of vehicles from the inventory heading
    """
    try:
        res = requests.get(start_url, headers=HEADERS, proxies=PROXIES)
        soup = BeautifulSoup(res.text, "html.parser")
        heading = soup.select_one("h1.inventoryheading")
        if not heading:
            raise Exception("Could not find inventory heading.")

        count_text = heading.get_text(strip=True)
        number = int(
            count_text.split(" ")[0]
        )  # Assumes first word is count (e.g., "105 used cars...")
        return number
    except Exception as e:
        print(f"Error getting total count: {str(e)}")
        return 0


def get_inventory_list():
    """
    Fetch all pages of results and return the complete inventory list
    """
    try:
        all_data = []
        total_vehicles = get_total_count()
        total_pages = math.ceil(total_vehicles / 25)
        print(f"Total vehicles: {total_vehicles} — Total pages: {total_pages}")

        for page_num in range(1, total_pages + 1):
            url = f"{base_url}/used-cars-in-columbus-oh/page/{page_num}"
            print(f"Scraping page {page_num}/{total_pages}...")

            res = requests.get(url, headers=HEADERS, proxies=PROXIES)
            soup = BeautifulSoup(res.text, "html.parser")
            cards = soup.find_all("div", class_="new-arrival")

            for card in cards:
                try:
                    a_tag = card.find("a", attrs={"data-cy": "inventory-link"})
                    if not a_tag:
                        continue

                    title = a_tag.get("title", "").strip()
                    link = base_url + a_tag.get("href", "").strip()

                    img_tag = a_tag.find("img")
                    image_url = img_tag["src"] if img_tag else ""

                    parent = card.find_parent("div", class_="card-body")
                    price_tag = parent.select_one(".label-price") if parent else None
                    price = price_tag.text.strip() if price_tag else "N/A"

                    mileage_tag = (
                        parent.select_one(".srp-miles div:last-child")
                        if parent
                        else None
                    )
                    mileage = mileage_tag.text.strip() if mileage_tag else "N/A"

                    all_data.append(
                        {
                            "title": title,
                            "link": link,
                            "price": price,
                            "mileage": mileage,
                            "image": image_url,
                        }
                    )

                except Exception as e:
                    print(f"Error parsing card: {e}")

            time.sleep(1)  # Polite delay

        print(f"\nTotal vehicles scraped: {len(all_data)}")
        return all_data
    except Exception as e:
        print(f"Error getting inventory list: {str(e)}")
        return []
