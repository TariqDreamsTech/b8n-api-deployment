import requests
from bs4 import BeautifulSoup
import math
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Base URL and settings
base_url = "https://www.elmwoodautosalesri.com/inventory"

# Headers and proxy settings
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "Referer": "https://www.elmwoodautosalesri.com/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

PROXIES = {
    "http": "http://henrywoowgraphics:udFdNect4I@185.240.121.143:50100",
    "https": "http://henrywoowgraphics:udFdNect4I@185.240.121.143:50100",
}


def create_session():
    """
    Create a requests session with retry logic
    """
    session = requests.Session()

    # Configure retry strategy
    retry_strategy = Retry(
        total=3,  # number of retries
        backoff_factor=1,  # wait 1, 2, 4 seconds between retries
        status_forcelist=[500, 502, 503, 504],  # HTTP status codes to retry on
    )

    # Mount the adapter with retry strategy
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


def fetch_inventory_page(page_num):
    """
    Fetch a single page of inventory
    """
    params = {"clearall": "1", "page": page_num}
    session = create_session()
    response = session.get(
        base_url, headers=HEADERS, params=params, proxies=PROXIES, verify=False
    )
    response.raise_for_status()
    return response.text


def get_total_pages(html, per_page=25):
    """
    Extract total number of pages from the HTML
    """
    soup = BeautifulSoup(html, "html.parser")
    summary = soup.select_one(".pager-summary")
    if summary:
        text = summary.get_text(strip=True)
        # Example format: Page: 1 of 2 (108 vehicles)
        if "(" in text:
            try:
                total_vehicles = int(text.split("(")[1].split()[0])
                return math.ceil(total_vehicles / per_page)
            except:
                pass
    return 1


def extract_vehicle_data(html):
    """
    Extract vehicle data from HTML
    """
    soup = BeautifulSoup(html, "html.parser")
    all_data = []

    for div in soup.select("div.i17r_mainInfo"):
        # Check if this vehicle has the problematic image
        # Look in the parent vehicle container for the image
        vehicle_container = div.find_parent("div", class_="i17r-vehicle-body") or div
        img_tag = (
            vehicle_container.select_one("img.i17r_mainImg")
            or vehicle_container.select_one("img#mainphoto")
            or vehicle_container.select_one("img.inv-image")
        )
        if img_tag and img_tag.has_attr("src"):
            img_src = img_tag["src"]
            print(f"Found image src: {img_src}")
            if "5146_newarrivalphoto.jpg" in img_src:
                print(f"⚠️  EXCLUDING vehicle with problematic image: {img_src}")
                continue  # Skip this vehicle record
        else:
            print("No image found for this vehicle")

        data = {}

        title_tag = div.select_one("h4.vehicleTitleH4 a")
        data["Title"] = title_tag.get_text(strip=True) if title_tag else None
        data["VDP URL"] = (
            "https://www.elmwoodautosalesri.com" + title_tag["href"]
            if title_tag and title_tag.has_attr("href")
            else None
        )

        trim_tag = div.select_one("a.i17r_TrimLevel")
        data["Trim"] = trim_tag.get_text(strip=True) if trim_tag else None

        price_tag = div.select_one("h2.lblPrice")
        data["Price"] = price_tag.get_text(strip=True) if price_tag else None

        def get_label_value(label_text):
            label = div.find("label", string=label_text)
            return label.find_next(text=True).strip() if label else None

        data["Stock"] = get_label_value("Stock #:")
        data["Mileage"] = get_label_value("Mileage:")
        data["Drive"] = get_label_value("Drive:")
        data["Transmission"] = get_label_value("Trans:")
        data["VIN"] = get_label_value("VIN:")
        data["Engine"] = get_label_value("Engine:")
        data["Cylinders"] = get_label_value("Cylinders:")
        data["Color"] = get_label_value("Color:")
        data["Interior"] = get_label_value("Interior:")
        data["Interior Color"] = get_label_value("Interior Color:")
        data["Fuel"] = get_label_value("Fuel:")

        # Carfax link (if exists)
        carfax = div.select_one("car-fax a[href]")
        data["Carfax URL"] = carfax["href"] if carfax else None

        all_data.append(data)

    return all_data


def get_inventory_list():
    """
    Fetch all pages of results and return the complete inventory list
    """
    try:
        # Fetch first page to determine total pages
        first_html = fetch_inventory_page(1)
        total_pages = get_total_pages(first_html)

        all_vehicles = extract_vehicle_data(first_html)

        for page in range(2, total_pages + 1):
            print(f"Fetching page {page} of {total_pages}")
            html = fetch_inventory_page(page)
            vehicles = extract_vehicle_data(html)
            all_vehicles.extend(vehicles)
            time.sleep(1)  # polite delay

        print(f"\nTotal vehicles scraped: {len(all_vehicles)}")
        return all_vehicles

    except Exception as e:
        print(f"Error getting inventory list: {str(e)}")
        return []
