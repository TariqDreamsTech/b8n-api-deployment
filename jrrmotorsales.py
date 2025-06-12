import requests
from bs4 import BeautifulSoup
import time

# Headers
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "cookie": "YOUR_COOKIE_HERE",
    "referer": "https://www.jrrmotorsales.com/inventory",
    "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
}

PROXIES = {
    "http": "http://henrywoowgraphics:udFdNect4I@185.240.121.143:50100",
    "https": "http://henrywoowgraphics:udFdNect4I@185.240.121.143:50100",
}


def get_inventory_list():
    """
    Fetch all pages of results and return the complete inventory list
    """
    try:
        results = []
        page = 1

        while True:
            url = f"https://www.jrrmotorsales.com/inventory?page={page}"
            print(f"Scraping Page {page}...")

            response = requests.get(url, headers=headers, proxies=PROXIES)
            soup = BeautifulSoup(response.text, "html.parser")

            vehicles = soup.find_all("div", class_="i10r_mainInfoWrap")

            if not vehicles:
                print("No vehicles found on this page. Stopping.")
                break

            for vehicle in vehicles:
                try:
                    title_tag = vehicle.find("h4", class_="i10r_vehicleTitle").find("a")
                    title = title_tag.get_text(strip=True)
                    href = title_tag["href"]

                    features = vehicle.find_all("div", class_="i10r_features")
                    color = (
                        features[0]
                        .find("p", class_="i10r_optColor")
                        .get_text(strip=True)
                        .replace("Color:", "")
                        .strip()
                    )
                    interior = (
                        features[0]
                        .find("p", class_="i10r_optInterior")
                        .get_text(strip=True)
                        .replace("Interior:", "")
                        .strip()
                    )
                    drive = (
                        features[0]
                        .find("p", class_="i10r_optDrive")
                        .get_text(strip=True)
                        .replace("Drive:", "")
                        .strip()
                    )
                    trans = (
                        features[0]
                        .find("p", class_="i10r_optTrans")
                        .get_text(strip=True)
                        .replace("Trans:", "")
                        .strip()
                    )

                    vin = (
                        features[1]
                        .find("p", class_="i10r_optVin")
                        .get_text(strip=True)
                        .replace("VIN:", "")
                        .strip()
                    )
                    engine = (
                        features[1]
                        .find("p", class_="i10r_optEngine")
                        .get_text(strip=True)
                        .replace("Engine:", "")
                        .strip()
                    )
                    mileage = (
                        features[1]
                        .find("p", class_="i10r_optMileage")
                        .get_text(strip=True)
                        .replace("Mileage:", "")
                        .strip()
                    )
                    stock = (
                        features[1]
                        .find("p", class_="i10r_optStock")
                        .get_text(strip=True)
                        .replace("Stock #:", "")
                        .strip()
                    )

                    price_tag = vehicle.find("div", class_="i10r_priceWrap")
                    price = price_tag.find("span", class_="price-2").get_text(
                        strip=True
                    )

                    results.append(
                        {
                            "title": title,
                            "link": f"https://www.jrrmotorsales.com{href}",
                            "color": color,
                            "interior": interior,
                            "drive": drive,
                            "transmission": trans,
                            "vin": vin,
                            "engine": engine,
                            "mileage": mileage,
                            "stock": stock,
                            "price": price,
                        }
                    )
                except Exception as e:
                    print("Error parsing vehicle:", e)

            # Check if "Next" button exists
            next_button = soup.find("button", {"aria-label": "Next"})
            if next_button and "disabled" not in next_button.attrs.get("class", []):
                page += 1
                time.sleep(1)  # be polite, avoid hammering the server
            else:
                print("No more pages.")
                break

        print(f"\nTotal vehicles scraped: {len(results)}")
        return results
    except Exception as e:
        print(f"Error getting inventory list: {str(e)}")
        return []
