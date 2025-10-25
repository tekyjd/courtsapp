"""
Ontario Courthouse Scraper – JSON-LD version
Pulls courthouse name, address, phone, fax, email from structured data.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time

def get_courthouse_links():
    url = "https://www.ontario.ca/locations/courts"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/119.0.0.0 Safari/537.36"
        )
    }

    print("📡 Fetching courthouse list...")
    res = requests.get(url, headers=headers, timeout=30)
    if res.status_code != 200:
        print(f"⚠️ Failed to fetch list ({res.status_code})")
        return []

    # Extract courthouse links (avoid anchors)
    links = sorted(set(re.findall(r'href="(/locations/courts/[0-9a-zA-Z\-]+)"', res.text)))
    full_links = [f"https://www.ontario.ca{l}" for l in links if not l.endswith("#")]
    print(f"✅ Found {len(full_links)} courthouse links")
    return full_links


def scrape_details(links):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/119.0.0.0 Safari/537.36"
        )
    }

    results = []
    for i, url in enumerate(links, start=1):
        print(f"🔎 [{i}/{len(links)}] {url}")
        try:
            res = requests.get(url, headers=headers, timeout=30)
            if res.status_code != 200:
                print(f"⚠️ Skipping ({res.status_code}) {url}")
                continue

            soup = BeautifulSoup(res.text, "html.parser")

            # Get JSON-LD structured data
            data_script = soup.find("script", type="application/ld+json")
            name = address = phone = fax = email = ""

            if data_script:
                try:
                    data = json.loads(data_script.string)
                    if isinstance(data, list):
                        data = data[0]

                    name = data.get("name", "")
                    address_block = data.get("address", {})
                    if isinstance(address_block, dict):
                        street = address_block.get("streetAddress", "")
                        city = address_block.get("addressLocality", "")
                        region = address_block.get("addressRegion", "")
                        postal = address_block.get("postalCode", "")
                        address = ", ".join(filter(None, [street, city, region, postal]))

                    phone = data.get("telephone", "")
                    fax = data.get("faxNumber", "")
                    email = data.get("email", "")
                except Exception as e:
                    print(f"⚠️ JSON parse error for {url}: {e}")

            if not name:
                # fallback to <h1>
                h1 = soup.find("h1")
                name = h1.get_text(strip=True) if h1 else ""

            results.append({
                "name": name,
                "url": url,
                "address": address,
                "phone": phone,
                "fax": fax,
                "email": email
            })
            time.sleep(1)

        except Exception as e:
            print(f"⚠️ Error fetching {url}: {e}")
            continue

    return results


def main():
    links = get_courthouse_links()
    if not links:
        print("❌ No courthouse links found — aborting.")
        return

    data = scrape_details(links)
    with open("courthouses.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Done. Saved {len(data)} courthouses to courthouses.json")


if __name__ == "__main__":
    main()
