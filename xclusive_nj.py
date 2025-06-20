import time
import requests
from bs4 import BeautifulSoup

# Proxy configuration
proxies = {
    "http": "http://henrywoowgraphics:udFdNect4I@185.240.121.143:50100",
    "https": "http://henrywoowgraphics:udFdNect4I@185.240.121.143:50100",
}

# Headers to mimic browser
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "Referer": "https://www.xclusivewholesale.com/",
}


# Base URL
def get_page_url(page):
    return f"https://www.xclusivenj.com/inventory/?page_no={page}"


# Fetch with retry logic
def safe_request(url, retries=3, timeout=15):
    for i in range(retries):
        try:
            return requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
        except Exception as e:
            print(f"Retry {i+1}/{retries} for {url}: {e}")
            time.sleep(2)
    return None


# Total vehicle pages
def get_total_pages():
    resp = safe_request(get_page_url(1))
    if resp and resp.ok:
        soup = BeautifulSoup(resp.text, "html.parser")
        vehicle_count = soup.select_one(".dws-vlp-total-vehicles")
        if vehicle_count:
            total = int("".join(filter(str.isdigit, vehicle_count.text)))
            return total, (total + 17) // 18  # 18 vehicles per page
    return 0, 0


# Extract vehicles
def parse_vehicles(html):
    soup = BeautifulSoup(html, "html.parser")
    results = []

    # Image URL to be excluded
    skip_image_src = "https://imagescf.dealercenter.net/320/240/202502-6d282c613bf24b2d953ba131f93c66e7.jpg"

    for v in soup.select(".vehicle-col"):
        img_tag = v.select_one(".vehicle-image")
        img_src = img_tag["src"] if img_tag else ""

        # Skip vehicle if the image matches the one to exclude
        if img_src == skip_image_src:
            continue

        def get_text(selector):
            el = v.select_one(selector)
            return el.text.strip() if el else ""

        results.append(
            {
                "title": get_text(".vehicle-title"),
                "price": get_text(".vehicle-price-value"),
                "stock": get_text(".vehicle-field-stocknumber .vehicle-info-value"),
                "drivetrain": get_text(".vehicle-field-drivetrain .vehicle-info-value"),
                "transmission": get_text(
                    ".vehicle-field-transmission .vehicle-info-value"
                ),
                "image": img_src,
                "link": (
                    v.select_one(".vehicle-title")["href"]
                    if v.select_one(".vehicle-title")
                    else ""
                ),
            }
        )

    return results


# Get total count
def get_inventory_count():
    total, _ = get_total_pages()
    return total


# Get inventory list
def get_inventory_list():
    total, pages = get_total_pages()
    print(f"Total Vehicles: {total} across {pages} pages")
    all_data = []
    for page in range(1, pages + 1):
        print(f"Scraping page {page}")
        resp = safe_request(get_page_url(page))
        if resp and resp.ok:
            all_data.extend(parse_vehicles(resp.text))
        else:
            print(f"Failed to get page {page}")
    return all_data


# Run the full scraper
def run_scraper():
    vehicles_data = get_inventory_list()
    print(f"Scraped {len(vehicles_data)} vehicles")
    return vehicles_data
