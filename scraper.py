"""
Fetch Ontario courthouse data directly from the Ontario.ca JSON API.
No Playwright or headless browser required.
"""

import requests
import json
from collections import defaultdict

def scrape():
    courthouses = []
    base_url = "https://www.ontario.ca/api/search"
    params = {
        "q": "",
        "filter": "locations",
        "sort": "title",
        "page": 1,
    }

    while True:
        res = requests.get(base_url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        if res.status_code != 200:
            print(f"⚠️ Request failed: {res.status_code}")
            break

        data = res.json()
        items = data.get("results", [])
        if not items:
            break

        for item in items:
            title = item.get("title", "").strip()
            address = item.get("address", {}).get("address_line", "").strip()
            if title and address:
                courthouses.append({"city": title, "address": address})

        if not data.get("next_page_url"):
            break
        params["page"] += 1

    # Deduplicate by city
    grouped = defaultdict(list)
    for ch in courthouses:
        grouped[ch["city"]].append(ch["address"])

    formatted = []
    for city, addresses in grouped.items():
        if len(addresses) == 1:
            formatted.append({"city": city, "address": addresses[0]})
        else:
            for addr in addresses:
                street = addr.split(",")[0].strip()
                formatted.append({"city": f"{city} ({street})", "address": addr})

    formatted.sort(key=lambda x: x["city"])

    with open("courthouses.json", "w", encoding="utf-8") as f:
        json.dump(formatted, f, ensure_ascii=False, indent=2)

    print(f"✅ Found {len(formatted)} courthouses")

if __name__ == "__main__":
    scrape()
