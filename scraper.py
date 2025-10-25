"""
Scrapes all courthouse names + page links from Ontario.ca,
bypassing their anti-bot protection by using full browser headers.
"""

import requests
import json

def scrape():
    url = "https://www.ontario.ca/locations/courts"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/119.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.ontario.ca/",
        "DNT": "1",
        "Connection": "keep-alive",
    }

    print("📡 Fetching main courthouse listing...")
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print(f"⚠️ Failed to fetch listing ({res.status_code})")
        with open("courthouse_links.json", "w") as f:
            json.dump([], f)
        return

    text = res.text
    if "views-row" not in text and "locations/courts/" not in text:
        print("⚠️ The page HTML did not include courthouse listings (likely JS-rendered).")
        with open("courthouse_links.json", "w") as f:
            json.dump([], f)
        return

    # extract all court URLs by pattern
    import re
    pattern = r'href="(/locations/courts/[^"]+)"'
    links = sorted(set(re.findall(pattern, text)))

    results = [
        {"url": "https://www.ontario.ca" + link}
        for link in links if link.startswith("/locations/courts/")
    ]

    print(f"✅ Found {len(results)} courthouse links")
    with open("courthouse_links.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape()
