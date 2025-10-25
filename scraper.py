"""
Fetch Ontario courthouse locations from Ontario's official open data portal.
This uses the CKAN API from data.ontario.ca.
"""

import requests
import json
from collections import defaultdict

def scrape():
    # CKAN API endpoint for the dataset
    api_url = "https://data.ontario.ca/api/3/action/package_show"
    params = {"id": "ontario-court-locations"}  # dataset ID slug

    print("📡 Fetching dataset metadata...")
    res = requests.get(api_url, params=params, headers={"User-Agent": "Mozilla/5.0"})
    if res.status_code != 200:
        print(f"⚠️ Failed to fetch dataset metadata ({res.status_code})")
        with open("courthouses.json", "w") as f:
            json.dump([], f)
        return

    dataset = res.json()
    if not dataset.get("success"):
        print("⚠️ Dataset fetch failed (invalid response)")
        with open("courthouses.json", "w") as f:
            json.dump([], f)
        return

    # Find the CSV resource in the dataset
    resources = dataset["result"]["resources"]
    csv_url = None
    for r in resources:
        if r["format"].lower() == "csv":
            csv_url = r["url"]
            break

    if not csv_url:
        print("⚠️ No CSV resource found in dataset")
        with open("courthouses.json", "w") as f:
            json.dump([], f)
        return

    print(f"📄 Downloading courthouse data from: {csv_url}")
    csv_data = requests.get(csv_url, headers={"User-Agent": "Mozilla/5.0"}).text

    # Parse CSV manually
    lines = [l.strip() for l in csv_data.splitlines() if l.strip()]
    header = [h.strip().lower() for h in lines[0].split(",")]
    city_index = header.index("municipality") if "municipality" in header else None
    address_index = header.index("address") if "address" in header else None

    courthouses = []
    if city_index is not None and address_index is not None:
        for line in lines[1:]:
            cols = [c.strip() for c in line.split(",")]
            if len(cols) > max(city_index, address_index):
                city = cols[city_index]
                address = cols[address_index]
                if city and address:
                    courthouses.append({"city": city, "address": address})

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
