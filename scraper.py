"""
Python script that scrapes the Ontario court listings and produces courthouses.json.
"""

import requests
from bs4 import BeautifulSoup
import json
from collections import defaultdict

def scrape():
    base_url = "https://www.ontario.ca/locations/courts?page="
    courthouses = []

    for page in range(0, 20):
        url = f"{base_url}{page}"
        res = requests.get(url)
        if res.status_code != 200:
            break

        soup = BeautifulSoup(res.text, "html.parser")
        rows = soup.select(".views-row")
        if not rows:
            break

        for item in rows:
            title_tag = item.select_one(".views-field-title a")
            address_tag = item.select_one(".views-field-field-location-address")
            if title_tag and address_tag:
                city = title_tag.get_text(strip=True)
                address = address_tag.get_text(" ", strip=True)
                courthouses.append({"city": city, "address": address})

    city_count = defaultdict(list)
    for ch in courthouses:
        city_count[ch["city"]].append(ch["address"])

    formatted = []
    for city, addresses in city_count.items():
        if len(addresses) == 1:
            formatted.append({"city": city, "address": addresses[0]})
        else:
            for addr in addresses:
                street = addr.split(",")[0].strip()
                formatted.append({"city": f"{city} ({street})", "address": addr})

    formatted.sort(key=lambda x: x["city"])
    with open("courthouses.json", "w", encoding="utf-8") as f:
        json.dump(formatted, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape()

