"""
Scrape Ontario courthouse names and contact page links directly
from the JSON feed used by https://www.ontario.ca/locations/courts
"""

import requests
import json

def scrape():
    # Ontario.ca JSON data feed (Drupal REST view)
    base_url = "https://www.ontario.ca"
    api_url = "https://www.ontario.ca/api/views/locations/courts?page={}"

    courthouses = []
    page = 0

    print("📡 Fetching courthouse data from Ontario.ca API feed...")

    while True:
        res = requests.get(api_url.format(page), headers={"User-Agent": "Mozilla/5.0"})
        if res.status_code != 200:
            print(f"⚠️ Page {page} request failed ({res.status_code})")
            break

        data = res.json()
        items = data.get("rows", [])
        if not items:
            break  # no more pages

        for item in items:
            title = item.get("title", "").strip()
            path = item.get("path", "").strip()
            if not path.startswith("http"):
                path = base_url + path
            courthouses.append({"name": title, "url": path})

        page += 1

    print(f"✅ Found {len(courthouses)} courthouses")

    with open("courthouse_links.json", "w", encoding="utf-8") as f:
        json.dump(courthouses, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape()
