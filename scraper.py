"""
Fetches Ontario courthouse locations from Ontario's open data catalogue
and writes them to courthouses.json.
"""

import requests
import json
from collections import defaultdict

def scrape():
    url = "https://www.ontario.ca/data/ontario-court-locations.json"
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

    if res.status_code != 200:
        print(f"⚠️ Request failed: {res.status_code}")
        with open("courthouses.json", "w") as f:
            json.dump([], f)
        return

    data = res.json()
    courthouses = []

    # Each record contains fields for city, address, etc.
    for record in data.get("data", []):
        city = record.get("City") or record.get("city") or record.get("Municipality") or ""
        address = record.get("Address") or record.get("address") or ""
        if city and address:
            courthouses.append({"city": city.strip(), "address": address.strip()})

    # Deduplicate
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
