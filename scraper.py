"""
Phase 2: Visit each courthouse page and extract details
(name, address, phone, fax, email).
Assumes courthouse_links.json already exists from Phase 1.
"""

import requests
from bs4 import BeautifulSoup
import json
import time

def scrape_details():
    # Load courthouse_links.json
    try:
        with open("courthouse_links.json", "r", encoding="utf-8") as f:
            links = json.load(f)
    except FileNotFoundError:
        print("❌ courthouse_links.json not found. Run Phase 1 first.")
        return

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/119.0.0.0 Safari/537.36"
        )
    }

    results = []
    for i, entry in enumerate(links, start=1):
        url = entry["url"]
        print(f"🔎 [{i}/{len(links)}] Fetching {url}")
        try:
            res = requests.get(url, headers=headers, timeout=30)
            if res.status_code != 200:
                print(f"⚠️  Skipping ({res.status_code}) {url}")
                continue

            soup = BeautifulSoup(res.text, "html.parser")

            # Courthouse name
            name = soup.select_one("h1").get_text(strip=True) if soup.select_one("h1") else ""

            # Address
            addr_el = soup.select_one(".field--name-field-location-address")
            address = addr_el.get_text(separator=" ", strip=True) if addr_el else ""

            # P
