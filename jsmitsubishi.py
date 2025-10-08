import math
import requests

PROXIES = {
    "http": "http://henrywoowgraphics:udFdNect4I@89.116.56.101:50100",
    "https": "http://henrywoowgraphics:udFdNect4I@89.116.56.101:50100",
}

url = "https://g58lko3etj-2.algolianet.com/1/indexes/production-inventory-global_price_asc/query?x-algolia-agent=Algolia%20for%20JavaScript%20(4.18.0)%3B%20Browser%20(lite)&x-algolia-api-key=cc3dce06acb2d9fc715bc10c9a624d80&x-algolia-application-id=G58LKO3ETJ"

headers = {
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Origin": "https://jsmitsubishi.com",
    "Referer": "https://jsmitsubishi.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded",
    "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
}

data_template = {
    "query": "",
    "clickAnalytics": True,
    "filters": 'car_condition:"used" AND functional_price <= 50500 AND is_active:true AND dealer_ids:"660" AND dealer_id:660<score=1> OR dealer_id:659<score=0> OR dealer_id:662<score=0> OR dealer_id:661<score=0>',
    "optionalFilters": [],
    "page": 0,
    "hitsPerPage": 36,
}


def get_inventory_count():
    """
    Fetch the total number of hits from page 0
    """
    try:
        response = requests.post(
            url, headers=headers, json=data_template, proxies=PROXIES
        )
        response.raise_for_status()
        result = response.json()
        nb_hits = result.get("nbHits", 0)
        print(f"Total hits found: {nb_hits}")
        return nb_hits
    except Exception as e:
        print(f"Error getting inventory count: {str(e)}")
        return 0


def get_inventory_list():
    """
    Fetch all pages of results and return the complete inventory list
    """
    try:
        nb_hits = get_inventory_count()
        hits_per_page = data_template["hitsPerPage"]
        total_pages = math.ceil(nb_hits / hits_per_page)
        all_hits = []

        for page in range(total_pages):
            print(f"Fetching page {page + 1}/{total_pages}")
            data_template["page"] = page
            response = requests.post(
                url, headers=headers, json=data_template, proxies=PROXIES
            )
            response.raise_for_status()
            result = response.json()
            hits = result.get("hits", [])
            all_hits.extend(hits)

        print(f"Total records fetched: {len(all_hits)}")
        return all_hits
    except Exception as e:
        print(f"Error getting inventory list: {str(e)}")
        return []
