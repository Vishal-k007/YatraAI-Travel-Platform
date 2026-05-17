"""
Fetch attraction images and save locally under frontend/public/images.

Uses Google Places API when GOOGLE_MAPS_API_KEY is set in backend/.env.
Otherwise uses Wikipedia/Wikimedia with rate-limit friendly delays.
"""
import json
import os
import re
import sqlite3
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "travel_platform.db"
IMAGES_DIR = BASE_DIR.parent / "frontend" / "public" / "images"
GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY") or os.getenv("GOOGLE_API_KEY")
USER_AGENT = "YatraAI/1.0 (educational travel app; contact: local)"

# Wikipedia article titles for primary image lookup
WIKIPEDIA_TITLES: dict[str, str] = {
    "Baga Beach": "Calangute",
    "Basilica of Bom Jesus": "Basilica of Bom Jesus (Goa)",
    "Dudhsagar Waterfalls": "Dudhsagar Falls",
    "Fort Aguada": "Fort Aguada",
    "Anjuna Flea Market": "Anjuna",
    "Club Cubana": "Nightlife in Goa",
    "Palolem Beach": "Palolem",
    "Spice Plantation": "Tourism in Goa",
    "Chapora Fort": "Chapora Fort",
    "Mangueshi Temple": "Shri Mangesh Temple",
    "Amber Fort": "Amer Fort",
    "Hawa Mahal": "Hawa Mahal",
    "City Palace": "City Palace, Jaipur",
    "Jantar Mantar": "Jantar Mantar, Jaipur",
    "Johari Bazaar": "Johari Bazaar",
    "Nahargarh Fort": "Nahargarh Fort",
    "Albert Hall Museum": "Albert Hall Museum, Jaipur",
    "Chokhi Dhani": "Chokhi Dhani",
    "Galtaji Temple (Monkey Temple)": "Galta Ji",
    "Bapu Bazaar": "Bapu Bazaar",
    "Solang Valley": "Solang Valley",
    "Hadimba Devi Temple": "Hidimba Devi Temple",
    "Rohtang Pass": "Rohtang Pass",
    "Old Manali": "Manali, Himachal Pradesh",
    "Vashisht Hot Water Springs": "Vashisht, Himachal Pradesh",
    "Jogini Waterfall": "Vashisht, Himachal Pradesh",
    "Manikaran Sahib": "Manikaran, Himachal Pradesh",
    "Mall Road": "Manali, Himachal Pradesh",
    "Bhrigu Lake": "Bhrigu Lake",
    "Naggar Castle": "Naggar Castle",
}

# Extra Wikimedia search queries when Wikipedia has no/few images
EXTRA_WIKIMEDIA_QUERIES: dict[str, str] = {
    "Baga Beach": "Baga Beach Calangute Goa",
    "Club Cubana": "Arpora Goa nightclub",
    "Spice Plantation": "Spice plantation Goa",
    "Anjuna Flea Market": "Anjuna market Goa",
    "Johari Bazaar": "Johari Bazaar Jaipur street",
    "Bapu Bazaar": "Bapu Bazaar Jaipur",
    "Old Manali": "Old Manali cafe street",
    "Jogini Waterfall": "Jogini waterfall Manali",
    "Mall Road": "Mall Road Manali street",
}


def safe_filename(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def api_get(url: str, params: dict, retries: int = 4) -> dict | None:
    for attempt in range(retries):
        try:
            res = requests.get(
                url,
                params=params,
                headers={"User-Agent": USER_AGENT},
                timeout=25,
            )
            if res.status_code == 429:
                wait = 5 * (attempt + 1)
                print(f"    Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            res.raise_for_status()
            return res.json()
        except Exception as exc:
            print(f"    API error (attempt {attempt + 1}): {exc}")
            time.sleep(3 * (attempt + 1))
    return None


def wikipedia_thumbnail(title: str) -> str | None:
    data = api_get(
        "https://en.wikipedia.org/w/api.php",
        {
            "action": "query",
            "titles": title,
            "prop": "pageimages",
            "piprop": "thumbnail",
            "pithumbsize": 960,
            "format": "json",
        },
    )
    if not data:
        return None
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        if "thumbnail" in page:
            return page["thumbnail"]["source"]
    return None


def wikimedia_search(query: str, limit: int = 3) -> list[str]:
    data = api_get(
        "https://commons.wikimedia.org/w/api.php",
        {
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": query,
            "gsrnamespace": "6",
            "gsrlimit": limit + 5,
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": 960,
        },
    )
    if not data:
        return []
    urls: list[str] = []
    skip = (".svg", ".pdf", ".ogg", ".webm", ".tif")
    for page in data.get("query", {}).get("pages", {}).values():
        if "imageinfo" not in page:
            continue
        title = page.get("title", "").lower()
        if any(title.endswith(ext) for ext in skip):
            continue
        info = page["imageinfo"][0]
        url = info.get("thumburl") or info.get("url")
        if url and url not in urls:
            urls.append(url)
        if len(urls) >= limit:
            break
    return urls


def fetch_google_places_photos(query: str, limit: int = 3) -> list[bytes]:
    if not GOOGLE_API_KEY:
        return []
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "places.photos",
    }
    try:
        res = requests.post(
            "https://places.googleapis.com/v1/places:searchText",
            headers=headers,
            json={"textQuery": query, "languageCode": "en", "maxResultCount": 1},
            timeout=25,
        )
        res.raise_for_status()
        places = res.json().get("places", [])
        if not places:
            return []
        images: list[bytes] = []
        for photo in places[0].get("photos", [])[:limit]:
            name = photo.get("name")
            if not name:
                continue
            media = requests.get(
                f"https://places.googleapis.com/v1/{name}/media",
                params={"maxWidthPx": 960, "key": GOOGLE_API_KEY},
                timeout=30,
                allow_redirects=True,
            )
            if media.status_code == 200 and media.content:
                images.append(media.content)
            time.sleep(0.5)
        return images
    except Exception as exc:
        print(f"    Google Places error: {exc}")
        return []


def collect_image_urls(name: str, city: str) -> list[str]:
    urls: list[str] = []

    wiki_title = WIKIPEDIA_TITLES.get(name)
    if wiki_title:
        thumb = wikipedia_thumbnail(wiki_title)
        time.sleep(2)
        if thumb:
            urls.append(thumb)

    extra_query = EXTRA_WIKIMEDIA_QUERIES.get(name, f"{name} {city} India")
    if len(urls) < 3:
        for url in wikimedia_search(extra_query, limit=3 - len(urls)):
            if url not in urls:
                urls.append(url)
            time.sleep(2)

    if len(urls) < 1:
        for url in wikimedia_search(f"{name} {city}", limit=3):
            if url not in urls:
                urls.append(url)
            time.sleep(2)

    return urls[:3]


def download_image(url: str, path: Path) -> bool:
    try:
        res = requests.get(url, timeout=30, headers={"User-Agent": USER_AGENT})
        if res.status_code == 200 and len(res.content) > 5000:
            path.write_bytes(res.content)
            return True
    except Exception as exc:
        print(f"    Download error: {exc}")
    return False


def process_attraction(attr_id: int, name: str, city: str, cursor, conn) -> bool:
    safe = safe_filename(name)
    saved: list[str] = []

    if GOOGLE_API_KEY:
        print("    Source: Google Maps Places API")
        query = f"{name}, {city}, India"
        for i, data in enumerate(fetch_google_places_photos(query, 3), start=1):
            path = IMAGES_DIR / f"{safe}_{i}.jpg"
            path.write_bytes(data)
            saved.append(f"/images/{path.name}")
    else:
        print("    Source: Wikipedia/Wikimedia")
        urls = collect_image_urls(name, city)
        for i, url in enumerate(urls, start=1):
            path = IMAGES_DIR / f"{safe}_{i}.jpg"
            if download_image(url, path):
                saved.append(f"/images/{path.name}")
            time.sleep(0.5)

    if not saved:
        return False

    while len(saved) < 3:
        saved.append(saved[0])

    cursor.execute(
        "UPDATE attractions SET image_url = ?, image_urls = ? WHERE id = ?",
        (saved[0], json.dumps(saved), attr_id),
    )
    conn.commit()
    print(f"    OK: {saved[0]}")
    return True


def main():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    rows = cursor.execute("SELECT id, name, city FROM attractions ORDER BY id").fetchall()

    source = "Google Maps" if GOOGLE_API_KEY else "Wikipedia/Wikimedia"
    print(f"Updating {len(rows)} attractions using {source}\n")

    ok = 0
    for attr_id, name, city in rows:
        print(f"[{attr_id}] {name}")
        if process_attraction(attr_id, name, city, cursor, conn):
            ok += 1
        time.sleep(3)

    conn.close()
    print(f"\nFinished: {ok}/{len(rows)} updated.")


if __name__ == "__main__":
    main()
