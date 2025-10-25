"""
Scrape all Ontario courthouse names and links via the Ontario.ca GraphQL endpoint.
"""

import requests
import json

def scrape():
    print("📡 Fetching Ontario courthouse data via GraphQL...")

    url = "https://www.ontario.ca/graphql"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json"
    }

    query = """
    {
      search(query: "courts", filter: { contentType: LOCATION }, limit: 200) {
        results {
          title
          path
        }
      }
    }
    """

    res = requests.post(url, headers=headers, json={"query": query})
    if res.status_code != 200:
        print(f"⚠️ GraphQL request failed ({res.status_code})")
        with open("courthouse_links.json", "w") as f:
            json.dump([], f)
        return

    data = res.json()
    results = data.get("data", {}).get("search", {}).get("results", [])
    courthouses = []

    for item in results:
        title = item.get("title", "").strip()
        path = item.get("path", "").strip()
        if title and "/locations/courts/" in path:
            full_url = f"https://www.ontario.ca{path}"
            courthouses.append({"name": title, "url": full_url})

    print(f"✅ Found {len(courthouses)} courthouse entries")

    with open("courthouse_links.json", "w", encoding="utf-8") as f:
        json.dump(courthouses, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape()
