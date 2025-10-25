"""
Phase 2 – Fetch address / phone / fax / email for each courthouse link.
Reads courthouse_links.json created by Phase 1.
"""

import requests
from bs4 import BeautifulSoup
import json
import time

def scrape_details():
    # Load links from previous phase
    try:
        with open("courthouse_links.json", "r", encoding="utf-8") as f:
            links = json.load(f)
    except FileNotFoundError:
        print("❌ courthouse_links.json not found — run link scraper first.")
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

            # Name
            name_el = soup.select_one("h1")
            name = name_el.get_text(strip=True) if name_el else ""

            # Address
            addr_el = soup.select_one(".field--name-field-location-address")
            address = addr_el.get_text(separator=" ", strip=True) if addr_el else ""

            # Contact section
            phone = fax = email = ""
            contact_el = soup.select_one(".field--name-field-phone-fax-email")
            if contact_el:
                for line in contact_el.get_text(separator="\n").split("\n"):
                    line = line.strip()
                    if "phone" in line.lower() or line.lower().startswith("tel"):
                        phone = line.split(":", 1)[-1].strip()
                    elif line.lower().startswith("fax"):
                        fax = line.split(":", 1)[-1].strip()
                    elif "@" in line:
                        email = line.strip()

            results.append({
                "name": name,
                "url": url,
                "address": address,
                "phone": phone,
                "fax": fax,
                "email": email
            })

            time.sleep(1)  # polite delay

        except Exception as e:
            print(f"⚠️ Error fetching {url}: {e}")
            continue  # move to next link

    with open("courthouses.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"✅ Done! Saved {len(results)} courthouses to courthouses.json")

if __name__ == "__main__":
    scrape_details()
