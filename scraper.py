"""
Scrape Ontario courthouse page links directly from the Ontario.ca XML sitemap.
This version needs only the 'requests' library.
"""

import requests
import xml.etree.ElementTree as ET
import json

def scrape():
    sitemap_url = "https://www.ontario.ca/sitemap.xml"
    base_url = "https://www.ontario.ca"

    print("📡 Downloading Ontario.ca sitemap...")
    res = requests.get(sitemap_url, headers={"User-Agent": "Mozilla/5.0"})
    if res.status_code != 200:
        print(f"⚠️ Failed to fetch sitemap ({res.status_code})")
        with open("courthouse_links.json", "w") as f:
            json.dump([], f)
        return

    # Parse XML
    root = ET.fromstring(res.text)
    ns = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    urls = []
    for loc in root.findall(".//ns:loc", ns):
        url = loc.text.strip()
        if "/locations/courts/" in url:
            urls.append(url)

    print(f"✅ Found {len(urls)} courthouse links")

    results = [{"url": u} for u in so]()
