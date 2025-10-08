import requests
import json
import re


# ---- Settings ----
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "text/html",
}

PROXIES = {
    "http": "http://henrywoowgraphics:udFdNect4I@89.116.56.101:50100",
    "https": "http://henrywoowgraphics:udFdNect4I@89.116.56.101:50100",
}


def get_total_vehicle_count():
    url = "https://www.pujolsautosale.com/inv-scripts-v2/inv/vehicles?vc=a&f=id%7csn%7cye%7cma%7cmo%7ctr%7cdt%7cta%7ctd%7cen%7cmi%7cdr%7cec%7cic%7cbt%7cpr%7cim%7ceq%7cvd%7cvin%7chpg%7ccpg%7cvc%7cco%7chi%7ccfx%7cacr%7cvt%7ccy%7cdi%7cft%7clo%7ccfk%7ctb%7ccs%7cnos%7csc%7cfp%7ccohd%7cnop%7cvdf%7cffmi%7ccfd%7cdc&ps=9&pn=0&sb=pr%7cd&sp=n&cb=dws_inventory_listing_4&fa=im%7cgt%7c1%2cim%7clt%7c1&dcid=18274604&h=62a7185fa48ec047c9c100a4e59ba4f1"

    try:
        response = requests.get(url, headers=HEADERS, proxies=PROXIES)
        json_match = re.search(r"dws_inventory_listing_4\((.*)\)", response.text)
        if json_match:
            json_str = json_match.group(1)
            json_data = json.loads(json_str)
            return json_data.get("TotalRecordCount")
        return None
    except Exception as e:
        print(f"Error getting vehicle count: {str(e)}")
        return None
