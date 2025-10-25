"""
Scrape all Ontario courthouse names and their contact-page links
from https://www.ontario.ca/locations/courts
"""

import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://www.ontario.ca"
LIST_URL = f"{BASE_URL}/locations/courts"

def scrape_links():
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    results = []

    print("📡 Fetching main court list...")
    res = session.get(LIST_URL)
    if res.status_code != 200:
        print(f"⚠️ Failed to load list page ({res.status_code})")
        return

    soup = BeautifulSoup(res.text, "html.parser")

    # Each courthouse is a link inside a views-row container
    for row in soup.select(".views-row"):
        link_tag = row.select_one(".views-field-title a")
        if not link_tag:
            continue

        name = link_tag.get_text(strip=True)
        href = link_tag["href"]
        full_link = href if href.startswith("http") else BASE_URL + href
        results.append({"name": name, "url": full_link})

    print(f"✅ Found {len(results)} courthouse links")

    with open("courthouse_links.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape_links()
