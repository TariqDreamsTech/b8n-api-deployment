import requests
import json

# ---- Settings ----
HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/json; charset=UTF-8",
    "Origin": "https://www.112autoplaza.com",
    "Referer": "https://www.112autoplaza.com/cars-for-sale-in-Patchogue-NY-Holtsville-East-Patchogue-Medford/used_cars",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}

COOKIES = {
    "ASP.NET_SessionId": "m3qzzmfa530snyhcy5va34zh",
}

PROXIES = {
    "http": "http://henrywoowgraphics:udFdNect4I@89.116.56.101:50100",
    "https": "http://henrywoowgraphics:udFdNect4I@89.116.56.101:50100",
}


# ---- JSON Payload Template ----
def get_base_payload():
    return {
        "params": {
            "DealerID": 4861,
            "StartRow": 0,
            "EndRow": 7000,
            "Year": "%",
            "Make": "%",
            "Makes": None,
            "Model": "%",
            "Price": "-1,200000000",
            "Stock": "%",
            "Mileage": "0,200000000",
            "Color": "%",
            "BodyType": "%",
            "VehicleType": "%",
            "VehicleTypeExclude": "-1",
            "NewVehiclePage": 1,
            "Lot": -1,
            "Special": 2,
            "PriceReduced": 2,
            "Sort": 12,
            "Cylinders": -1,
            "Transmission": "%",
            "VehicleStatus": -1,
            "DealerCity": "",
            "SkipSoldCheck": 0,
            "DriveTrain": "%",
            "FTS": "",
            "InvVehicleStatus": "0",
            "FuelType": "%",
            "InteriorColor": "%",
            "InventorySearch": False,
            "MultiSelect": False,
            "CurrentPageNumber": "1",
            "MakeModelOnly": 1,
        }
    }


# ---- Get Total Vehicle Count ----
def get_inventory_count():
    url = "https://www.112autoplaza.com/0/DealerWebLib/DealerWebService.asmx/GetInventoryPaging"
    payload = get_base_payload()
    payload["params"]["StartRow"] = 0
    payload["params"]["EndRow"] = 1  # Minimal request to get the count

    try:
        response = requests.post(
            url, headers=HEADERS, cookies=COOKIES, json=payload, proxies=PROXIES
        )
        response.raise_for_status()
        json_data = response.json()
        total_count = json_data.get("d", {}).get("InvMinMax", {}).get("Count", 0)
        print(f"Total Vehicles: {total_count}")
        return total_count
    except Exception as e:
        print(f"Error getting vehicle count: {str(e)}")
        return 0


# ---- Get Inventory Page List ----
def get_inventory_page_list(start_row, end_row):
    url = "https://www.112autoplaza.com/0/DealerWebLib/DealerWebService.asmx/GetInventoryPaging"
    payload = get_base_payload()
    payload["params"]["StartRow"] = start_row
    payload["params"]["EndRow"] = end_row

    try:
        response = requests.post(
            url, headers=HEADERS, cookies=COOKIES, json=payload, proxies=PROXIES
        )
        response.raise_for_status()
        json_data = response.json()
        inv_page_list = json_data.get("d", {}).get("InvPageList", [])
        return inv_page_list
    except Exception as e:
        print(f"Error getting vehicle inventory: {str(e)}")
        return []
