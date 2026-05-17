"""Build curated image URL map for attractions (slow, rate-limit safe)."""
import json
import time
from pathlib import Path

import requests

USER_AGENT = "YatraAI/1.0"
OUT = Path(__file__).parent / "place_images_curated.json"

ATTRACTIONS = [
    ("Baga Beach", "Goa", "Baga Beach Calangute Goa"),
    ("Basilica of Bom Jesus", "Goa", "Basilica of Bom Jesus Goa"),
    ("Dudhsagar Waterfalls", "Goa", "Dudhsagar Falls Goa"),
    ("Fort Aguada", "Goa", "Fort Aguada Goa"),
    ("Anjuna Flea Market", "Goa", "Anjuna flea market Goa"),
    ("Club Cubana", "Goa", "Club Cubana Arpora Goa"),
    ("Palolem Beach", "Goa", "Palolem Beach Goa"),
    ("Spice Plantation", "Goa", "Sahakari Spice Farm Goa"),
    ("Chapora Fort", "Goa", "Chapora Fort Goa"),
    ("Mangueshi Temple", "Goa", "Shri Mangesh Temple Goa"),
    ("Amber Fort", "Jaipur", "Amber Fort Amer Jaipur"),
    ("Hawa Mahal", "Jaipur", "Hawa Mahal Jaipur"),
    ("City Palace", "Jaipur", "City Palace Jaipur"),
    ("Jantar Mantar", "Jaipur", "Jantar Mantar Jaipur"),
    ("Johari Bazaar", "Jaipur", "Johari Bazaar Jaipur"),
    ("Nahargarh Fort", "Jaipur", "Nahargarh Fort Jaipur"),
    ("Albert Hall Museum", "Jaipur", "Albert Hall Museum Jaipur"),
    ("Chokhi Dhani", "Jaipur", "Chokhi Dhani Jaipur"),
    ("Galtaji Temple (Monkey Temple)", "Jaipur", "Galtaji temple Jaipur"),
    ("Bapu Bazaar", "Jaipur", "Bapu Bazaar Jaipur"),
    ("Solang Valley", "Manali", "Solang Valley Manali"),
    ("Hadimba Devi Temple", "Manali", "Hidimba Devi Temple Manali"),
    ("Rohtang Pass", "Manali", "Rohtang Pass Himachal"),
    ("Old Manali", "Manali", "Old Manali Himachal"),
    ("Vashisht Hot Water Springs", "Manali", "Vashisht hot springs Manali"),
    ("Jogini Waterfall", "Manali", "Jogini waterfall Manali"),
    ("Manikaran Sahib", "Manali", "Manikaran Sahib Gurudwara"),
    ("Mall Road", "Manali", "Mall Road Manali"),
    ("Bhrigu Lake", "Manali", "Bhrigu Lake Himachal"),
    ("Naggar Castle", "Manali", "Naggar Castle Himachal"),
]


def commons_urls(query: str, limit: int = 3) -> list[str]:
    for attempt in range(5):
        try:
            r = requests.get(
                "https://commons.wikimedia.org/w/api.php",
                params={
                    "action": "query",
                    "format": "json",
                    "generator": "search",
                    "gsrsearch": query,
                    "gsrnamespace": "6",
                    "gsrlimit": limit + 6,
                    "prop": "imageinfo",
                    "iiprop": "url",
                    "iiurlwidth": 960,
                },
                headers={"User-Agent": USER_AGENT},
                timeout=25,
            )
            if r.status_code == 429:
                time.sleep(8 * (attempt + 1))
                continue
            r.raise_for_status()
            urls = []
            for p in r.json().get("query", {}).get("pages", {}).values():
                if "imageinfo" not in p:
                    continue
                t = p.get("title", "").lower()
                if any(t.endswith(x) for x in (".svg", ".pdf", ".ogg")):
                    continue
                u = p["imageinfo"][0].get("thumburl") or p["imageinfo"][0].get("url")
                if u and u not in urls:
                    urls.append(u)
                if len(urls) >= limit:
                    break
            return urls
        except Exception as e:
            print(f"  err {e}")
            time.sleep(5)
    return []


def main():
    data = {}
    if OUT.exists():
        data = json.loads(OUT.read_text(encoding="utf-8"))

    for name, city, query in ATTRACTIONS:
        if name in data and len(data[name]) >= 3:
            print(f"skip {name}")
            continue
        print(f"fetch {name}...")
        urls = commons_urls(query, 3)
        if len(urls) < 3:
            urls += commons_urls(f"{name} {city}", 3 - len(urls))
        urls = list(dict.fromkeys(urls))[:3]
        if urls:
            data[name] = urls
            OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
            print(f"  got {len(urls)}")
        else:
            print("  FAILED")
        time.sleep(8)

    print(f"Saved {len(data)} attractions to {OUT}")


if __name__ == "__main__":
    main()
