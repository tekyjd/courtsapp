"""
Scrapes Ontario courthouse addresses from ontario.ca/locations/courts
and saves them as courthouses.json for public use.
"""

import requests
from bs4 import BeautifulSoup
import json
from collections import defaultdict

def scrape():
    base_url = "https://www.ontario.ca/locations/courts?page="
    courthouses = []

    for page in range(0, 15):  # 10+ pages of results
        url = f"{base_url}{page}"
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if res.status_code != 200:
            break

        soup = BeautifulSoup(res.text, "html.parser")

        # each courthouse container
        items = soup.select("div.location-listing, div.views-row")
        if not items:
            break

        for item in items:
            # courthouse name
            name_tag = item.select_one("a.location-title, .views-field-title a")
            # address
            address_tag = item.select_one(".location-address, .views-field-field-location-address")

            if name_tag and address_tag:
                city = name_tag.get_text(strip=True)
                address = " ".join(address_tag.get_text(separator=" ", strip=True).split())
                courthouses.append({"city": city, "address": address})

    # deduplicate and group
    city_map = defaultdict(list)
    for ch in courthouses:
        city_map[ch["city"]].append(ch["address"])

    formatted = []
    for city, addrs in city_map.items():
        if len(addrs) == 1:
            formatted.append({"city": city, "address": addrs[0]})
        else:
            for addr in addrs:
                street = addr.split(",")[0].strip()
                formatted.append({"city": f"{city} ({street})", "address": addr})

    formatted.sort(key=lambda x: x["city"])

    with open("courthouses.json", "w", encoding="utf-8") as f:
        json.dump(formatted, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {len(formatted)} courthouses.")

if __name__ == "__main__":
    scrape()
