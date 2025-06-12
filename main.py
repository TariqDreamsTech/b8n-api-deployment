from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlunparse, urlencode, urlparse
import json
import re
import time
from tota_vehicle_count import get_total_vehicle_count
from autoplaza import get_inventory_count, get_inventory_page_list
from jsmitsubishi import (
    get_inventory_count as get_jsmitsubishi_count,
    get_inventory_list,
)
from elmoraautosales2 import (
    get_inventory_count as get_elmora_count,
    get_inventory_list as get_elmora_list,
)
from jrrmotorsales import get_inventory_list as get_jrr_list

app = FastAPI()

# ---- Settings ----
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "text/html",
}

PROXIES = {
    "http": "http://henrywoowgraphics:udFdNect4I@185.240.121.143:50100",
    "https": "http://henrywoowgraphics:udFdNect4I@185.240.121.143:50100",
}

total_vehicles_count = get_total_vehicle_count()


# ---- Request Model ----
class ScrapeInput(BaseModel):
    password: str

    class Config:
        json_schema_extra = {"example": {"password": "0724"}}


class AutoplazaRequest(BaseModel):
    password: str

    class Config:
        json_schema_extra = {"example": {"password": "0724"}}


class JSMitsubishiRequest(BaseModel):
    password: str

    class Config:
        json_schema_extra = {"example": {"password": "0724"}}


class ElmoraAutoSales2Request(BaseModel):
    password: str

    class Config:
        json_schema_extra = {"example": {"password": "0724"}}


class JRRMotorSalesRequest(BaseModel):
    password: str

    class Config:
        json_schema_extra = {"example": {"password": "0724"}}


# ---- Utilities ----
def extract_json_from_jsonp(text):
    try:
        match = re.search(r"dws_inventory_listing_4\((\{.*?\})\)", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    except Exception as e:
        print("❌ JSON extraction failed:", e)
    return None


def safe_request(url, retries=3, timeout=30):
    for attempt in range(retries):
        try:
            response = requests.get(
                url, headers=HEADERS, proxies=PROXIES, timeout=timeout
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"⚠ Retry {attempt+1}/{retries} failed for: {url}")
            time.sleep(2)
    print(f"❌ Skipping after {retries} failed attempts: {url}")
    return None


# ---- Scrape Route ----
@app.post("/scrape")
async def scrape(data: ScrapeInput):
    # Verify password
    if data.password != "0724":
        raise HTTPException(status_code=401, detail="Invalid password")

    base_url = "https://www.pujolsautosale.com/inventory/"
    pager = 9  # Default pager value

    total_pages = (total_vehicles_count + pager - 1) // pager

    unique_urls = set()

    # Step 1: Collect vehicle JSONP URLs
    for page_no in range(1, total_pages + 1):
        parsed = urlparse(base_url)
        query = urlencode({"page_no": page_no, "pager": pager})
        page_url = urlunparse(parsed._replace(query=query))

        print(f"\n🔎 Fetching inventory page {page_no}: {page_url}")
        resp = safe_request(page_url)
        if not resp:
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup.find_all(["a", "script", "link", "img", "form"]):
            for attr in ["href", "src", "action"]:
                url = tag.get(attr)
                if url:
                    full_url = urljoin(page_url, url)
                    if "inv-scripts-v2/inv/vehicles" in full_url.lower():
                        unique_urls.add(full_url)

    print(f"\n🔗 Total unique vehicle data URLs found: {len(unique_urls)}")

    # Step 2: Fetch vehicle data
    all_vehicles = []
    for url in unique_urls:
        print(f"\n🚗 Fetching vehicle data: {url}")
        resp = safe_request(url)
        if not resp:
            continue

        json_data = extract_json_from_jsonp(resp.text)
        if json_data and "Vehicles" in json_data:
            all_vehicles.extend(json_data["Vehicles"])
            print(f"✅ Extracted {len(json_data['Vehicles'])} vehicles.")
        else:
            print("⚠ No vehicle data found in response.")

    print(f"\n🎉 Total vehicles collected: {len(all_vehicles)}")
    return {"count": len(all_vehicles), "vehicles": all_vehicles}


@app.post("/autoplaza")
async def get_autoplaza_inventory(request: AutoplazaRequest):
    if request.password != "0724":  # Using the same password as the scrape endpoint
        raise HTTPException(status_code=401, detail="Invalid password")

    try:
        # Get total count first
        total_count = get_inventory_count()

        # Get all inventory (using default range)
        inventory = get_inventory_page_list(
            0, 7000
        )  # Using max range from base payload

        return {"total_count": total_count, "inventory": inventory}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/jsmitsubishi")
async def get_jsmitsubishi_inventory(request: JSMitsubishiRequest):
    if request.password != "0724":  # Using the same password as other endpoints
        raise HTTPException(status_code=401, detail="Invalid password")

    try:
        # Get total count first
        total_count = get_jsmitsubishi_count()

        # Get all inventory
        inventory = get_inventory_list()

        return {"total_count": total_count, "inventory": inventory}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/elmoraautosales2")
async def get_elmora_inventory(request: ElmoraAutoSales2Request):
    if request.password != "0724":  # Using the same password as other endpoints
        raise HTTPException(status_code=401, detail="Invalid password")

    try:

        # Get all inventory
        inventory = get_elmora_list()

        return {"inventory": inventory}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/jrrmotorsales")
async def get_jrr_inventory(request: JRRMotorSalesRequest):
    if request.password != "0724":  # Using the same password as other endpoints
        raise HTTPException(status_code=401, detail="Invalid password")

    try:
        # Get all inventory
        inventory = get_jrr_list()

        return {"inventory": inventory}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
