"""Apply curated place image URLs to the database (no bulk download)."""
import json
import sqlite3
from pathlib import Path
from urllib.parse import urlparse, urlunparse

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "travel_platform.db"
CURATED_PATH = BASE_DIR / "place_images_curated.json"

MANUAL_URLS: dict[str, list[str]] = {
    "Club Cubana": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Tito%27s_Lane%2C_Baga_Beach%2C_Goa.jpg/960px-Tito%27s_Lane%2C_Baga_Beach%2C_Goa.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Baga_Beach%2C_Calangute%2C_Goa.jpg/960px-Baga_Beach%2C_Calangute%2C_Goa.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Anjuna%2C_Goa%2C_India%2C_Anjuna_Flea_Market.jpg/960px-Anjuna%2C_Goa%2C_India%2C_Anjuna_Flea_Market.jpg",
    ],
    "Bapu Bazaar": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/East_facade_Hawa_Mahal_Jaipur_from_ground_level.jpg/960px-East_facade_Hawa_Mahal_Jaipur_from_ground_level.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Johari_Bazaar%2C_Jaipur.jpg/960px-Johari_Bazaar%2C_Jaipur.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Jaipur_03-2016_11_Hawa_Mahal.jpg/960px-Jaipur_03-2016_11_Hawa_Mahal.jpg",
    ],
    "Vashisht Hot Water Springs": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Vashisht_Temple%2C_Manali.jpg/960px-Vashisht_Temple%2C_Manali.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Solang_Valley_%2CManali%2C_Himachal_Pradesh.jpg/960px-Solang_Valley_%2CManali%2C_Himachal_Pradesh.jpg",
    ],
}


def clean_url(url: str) -> str:
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))


def main():
    curated = json.loads(CURATED_PATH.read_text(encoding="utf-8"))
    curated.update(MANUAL_URLS)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    rows = cursor.execute("SELECT id, name FROM attractions ORDER BY id").fetchall()

    ok = 0
    for attr_id, name in rows:
        raw_urls = curated.get(name)
        if not raw_urls:
            print(f"[{attr_id}] {name} - skipped (no URLs)")
            continue

        urls = [clean_url(u) for u in raw_urls[:3]]
        while len(urls) < 3:
            urls.append(urls[0])

        cursor.execute(
            "UPDATE attractions SET image_url = ?, image_urls = ? WHERE id = ?",
            (urls[0], json.dumps(urls), attr_id),
        )
        print(f"[{attr_id}] {name}")
        ok += 1

    conn.commit()
    conn.close()
    print(f"\nUpdated {ok}/{len(rows)} attractions with curated image URLs.")


if __name__ == "__main__":
    main()
