import requests
from bs4 import BeautifulSoup
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Base URL and settings
base_url = "https://www.jrrmotorsales.com"
DEFAULT_IMAGE_URL = (
    "https://imagescdn.dealercarsearch.com/DealerImages/23149/23149_newarrivalphoto.jpg"
)

# Headers and proxy settings
HEADERS = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
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


def get_inventory_list():
    """
    Fetch all pages of results and return the complete inventory list
    """
    try:
        results = []
        page = 1
        session = create_session()

        while True:
            url = f"{base_url}/inventory?page={page}"
            print(f"Scraping Page {page}...")

            try:
                response = session.get(
                    url,
                    headers=HEADERS,
                    proxies=PROXIES,
                    verify=False,  # Disable SSL verification
                    timeout=30,
                )
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error fetching page {page}: {str(e)}")
                time.sleep(5)  # Wait longer on error
                continue

            soup = BeautifulSoup(response.text, "html.parser")

            vehicles = soup.find_all("div", class_="invMainCell")
            if not vehicles:
                print("No vehicles found. Stopping.")
                break

            for vehicle in vehicles:
                try:
                    # Get image
                    img_div = vehicle.find("div", class_="i10r_image")
                    img_tag = img_div.find("img")
                    img_url = img_tag["src"] if img_tag else ""

                    if img_url == DEFAULT_IMAGE_URL:
                        continue  # Skip default image listings

                    # Get vehicle title & link
                    info_div = vehicle.find("div", class_="i10r_mainWrap")
                    title_tag = info_div.find("h4", class_="i10r_vehicleTitle").find(
                        "a"
                    )
                    title = title_tag.get_text(strip=True)
                    href = title_tag["href"]

                    # Get all feature blocks
                    feature_blocks = info_div.find_all("div", class_="i10r_features")

                    color = (
                        feature_blocks[0]
                        .find("p", class_="i10r_optColor")
                        .get_text(strip=True)
                        .split(":", 1)[-1]
                        .strip()
                    )
                    interior = (
                        feature_blocks[0]
                        .find("p", class_="i10r_optInterior")
                        .get_text(strip=True)
                        .split(":", 1)[-1]
                        .strip()
                    )
                    drive = (
                        feature_blocks[0]
                        .find("p", class_="i10r_optDrive")
                        .get_text(strip=True)
                        .split(":", 1)[-1]
                        .strip()
                    )
                    trans = (
                        feature_blocks[0]
                        .find("p", class_="i10r_optTrans")
                        .get_text(strip=True)
                        .split(":", 1)[-1]
                        .strip()
                    )

                    vin = (
                        feature_blocks[1]
                        .find("p", class_="i10r_optVin")
                        .get_text(strip=True)
                        .split(":", 1)[-1]
                        .strip()
                    )
                    engine = (
                        feature_blocks[1]
                        .find("p", class_="i10r_optEngine")
                        .get_text(strip=True)
                        .split(":", 1)[-1]
                        .strip()
                    )
                    mileage = (
                        feature_blocks[1]
                        .find("p", class_="i10r_optMileage")
                        .get_text(strip=True)
                        .split(":", 1)[-1]
                        .strip()
                    )
                    stock = (
                        feature_blocks[1]
                        .find("p", class_="i10r_optStock")
                        .get_text(strip=True)
                        .split(":", 1)[-1]
                        .strip()
                    )

                    # Price
                    price = info_div.find("span", class_="price-2").get_text(strip=True)

                    results.append(
                        {
                            "title": title,
                            "link": f"{base_url}{href}",
                            "color": color,
                            "interior": interior,
                            "drive": drive,
                            "transmission": trans,
                            "vin": vin,
                            "engine": engine,
                            "mileage": mileage,
                            "stock": stock,
                            "price": price,
                            "image": img_url,
                        }
                    )

                except Exception as e:
                    print(f"Error parsing vehicle: {str(e)}")

            # Pagination logic
            next_btn = soup.find("button", {"aria-label": "Next"})
            if next_btn and "disabled" not in next_btn.get("class", []):
                page += 1
                time.sleep(2)  # Increased delay between pages
            else:
                print("No more pages.")
                break

        print(f"\nTotal vehicles scraped: {len(results)}")
        return results

    except Exception as e:
        print(f"Error getting inventory list: {str(e)}")
        return []
