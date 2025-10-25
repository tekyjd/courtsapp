"""
Scrape Ontario courthouse data using Playwright (renders JS).
"""

import asyncio
import json
from playwright.async_api import async_playwright
from collections import defaultdict

async def scrape():
    courthouses = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        for page_num in range(0, 10):
            url = f"https://www.ontario.ca/locations/courts?page={page_num}"
            await page.goto(url)
            await page.wait_for_selector(".location-listing, .views-row", timeout=15000)
            html = await page.content()

            items = await page.query_selector_all(".location-listing, .views-row")
            if not items:
                break

            for item in items:
                name_el = await item.query_selector("a.location-title, .views-field-title a")
                addr_el = await item.query_selector(".location-address, .views-field-field-location-address")
                if name_el and addr_el:
                    city = (await name_el.inner_text()).strip()
                    address = (await addr_el.inner_text()).strip().replace("\\n", " ")
                    courthouses.append({"city": city, "address": address})

        await browser.close()

    # dedupe
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
                formatted.append({"city": f\"{city} ({street})\", \"address\": addr})

    formatted.sort(key=lambda x: x["city"])
    with open("courthouses.json", "w", encoding="utf-8") as f:
        json.dump(formatted, f, ensure_ascii=False, indent=2)

    print(f"✅ Found {len(formatted)} courthouses")

if __name__ == "__main__":
    asyncio.run(scrape())
