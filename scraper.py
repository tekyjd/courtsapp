"""
Full Ontario courthouse scraper.
Collects courthouse name, page link, address, phone, fax, and email
from https://www.ontario.ca/locations/courts
"""

import json
from playwright.sync_api import sync_playwright

BASE_URL = "https://www.ontario.ca"
LIST_URL = f"{BASE_URL}/locations/courts"

def scrape():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("📡 Loading main courthouse list...")
        page.goto(LIST_URL, timeout=60000)
        page.wait_for_selector(".views-field-title a")

        links = page.query_selector_all(".views-field-title a")
        print(f"🔗 Found {len(links)} courthouse links")

        for i, link in enumerate(links, start=1):
            name = link.inner_text().strip()
            href = link.get_attribute("href")
            if not href:
                continue
            full_link = href if href.startswith("http") else BASE_URL + href

            print(f"➡️ [{i}/{len(links)}] Scraping {name}")

            # Visit the courthouse page
            detail = browser.new_page()
            try:
                detail.goto(full_link, timeout=60000)
                detail.wait_for_selector(".field--name-field-location-address", timeout=10000)
            except Exception:
                print(f"⚠️ Skipping {name} (page timeout)")
                detail.close()
                continue

            # Address
            addr_el = detail.query_selector(".field--name-field-location-address")
            address = addr_el.inner_text().strip() if addr_el else ""

            # Contact details
            phone = fax = email = ""
            contact_section = detail.query_selector(".field--name-field-phone-fax-email")
            if contact_section:
                text = contact_section.inner_text()
                for line in text.splitlines():
                    line = line.strip()
                    if line.lower().startswith("tel:") or line.lower().startswith("phone"):
                        phone = line.split(":", 1)[-1].strip()
                    elif line.lower().startswith("fax"):
                        fax = line.split(":", 1)[-1].strip()
                    elif "@" in line:
                        email = line.strip()

            results.append({
                "name": name,
                "url": full_link,
                "address": address,
                "phone": phone,
                "fax": fax,
                "email": email
            })

            detail.close()

        browser.close()

    with open("courthouses.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"✅ Done! Saved {len(results)} courthouse records to courthouses.json")

if __name__ == "__main__":
    scrape()
