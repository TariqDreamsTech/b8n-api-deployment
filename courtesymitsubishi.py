import requests
import json


def get_courtesymitsubishi_list():
    """
    Fetch vehicle inventory from Courtesy Mitsubishi API
    Returns a list of vehicles with model, year, and price information
    """
    url = "https://hippo.prod.core.autofi.io/api/v2/vehicles"

    headers = {
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9",
        "autofiservice": "autofi-panda-prod:vehiclesV2",
        "content-type": "application/json",
        "dealers": "DET6",
        "origin": "https://www.courtesymitsubishima.com",
        "priority": "u=1, i",
        "referer": "https://www.courtesymitsubishima.com/search/used-attleboro-ma/",
        "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    }

    # Common payload settings
    payload_template = {
        "filters": {"dealer": ["DET6"]},
        "format": "json",
        "fields": [
            "age",
            "algModel",
            "algStyle",
            "baseMsrp",
            "bodyType",
            "bookValue",
            "color",
            "cost",
            "dealerCode",
            "dealerName",
            "dealerRetailPrice",
            "dealerRoutingPriority",
            "discount",
            "driveTrain",
            "fuelType",
            "invoice",
            "make",
            "maxDealerCash",
            "mileage",
            "model",
            "modelCode",
            "msrp",
            "packageCode",
            "photoUrls",
            "preInstalledAccessories",
            "rawDiscount",
            "sellingPrice",
            "stockNumber",
            "trim",
            "trimCode",
            "updatedAt",
            "vin",
            "year",
        ],
        "limit": 100,
        "offset": 0,
    }

    all_vehicles = []
    page = 0

    while True:
        payload = payload_template.copy()
        payload["offset"] = page * payload["limit"]

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code != 200:
                print(f"Request failed at page {page}. Status: {response.status_code}")
                break

            data = response.json()
            vehicles = data.get("data", {}).get("vehicles", [])

            if not vehicles:
                break  # No more data

            all_vehicles.extend(vehicles)
            print(f"Fetched page {page + 1} with {len(vehicles)} vehicles")

            page += 1

        except Exception as e:
            print(f"Error fetching page {page}: {str(e)}")
            break

    print(f"\n✅ Total vehicles fetched: {len(all_vehicles)}")

    # Format vehicles for display
    formatted_vehicles = []
    for vehicle in all_vehicles:
        model = (vehicle.get("model") or "").lower().replace(" ", "-")
        year = vehicle.get("year")
        price = vehicle.get("sellingPrice")
        make = (vehicle.get("make") or "").lower().replace(" ", "-")
        trim = (vehicle.get("trim") or "").lower().replace(" ", "-")
        stock = vehicle.get("stockNumber")

        # Skip if any of the essentials are missing
        if not all([model, year, price, make, trim, stock]):
            continue

        formatted_vehicle = {
            "year": year,
            "make": make.title(),
            "model": model.title(),
            "price": price,
        }

        formatted_vehicles.append(formatted_vehicle)
        print(f"{year} {make.title()} {model.title()} - ${price}")

    return formatted_vehicles
