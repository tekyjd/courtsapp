"""
Ontario Courthouse Scraper – API version (final)
Gets courthouse details directly from Ontario.ca's content API.
"""

import requests
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

    # Extract courthouse URLs
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
        match = re.search(r"/courts/(\d+)-", url)
        if not match:
            continue

        node_id = match.group(1)
        api_url = f"https://www.ontario.ca/api/node/{node_id}.json"
        print(f"🔎 [{i}/{len(links)}] {url} -> {api_url}")

        try:
            res = requests.get(api_url, headers=headers, timeout=30)
            if res.status_code != 200:
                print(f"⚠️ Skipping ({res.status_code}) {api_url}")
                continue

            data = res.json()
            name = data.get("title", "")
            address = ""
            phone = fax = email = ""

            # Address structure
            addr = data.get("field_location_address", {})
            if isinstance(addr, dict):
                street = addr.get("thoroughfare", "")
                city = addr.get("locality", "")
                region = addr.get("administrative_area", "")
                postal = addr.get("postal_code", "")
                address = ", ".join(filter(None, [street, city, region, postal]))

            phone = data.get("field_phone", "")
            fax = data.get("field_fax", "")
            email = data.get("field_email", "")

            results.append({
                "name": name,
                "url": url,
                "address": address,
                "phone": phone,
                "fax": fax,
                "email": email
            })

            time.sleep(0.5)

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
