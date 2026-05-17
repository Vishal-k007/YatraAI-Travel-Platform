import os
import json
import time
import requests
import sqlite3

db_path = r"c:\Users\Vishal\OneDrive\Desktop\pdd app\backend\travel_platform.db"
images_dir = r"c:\Users\Vishal\OneDrive\Desktop\pdd app\frontend\public\images"
os.makedirs(images_dir, exist_ok=True)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT id, name, city FROM attractions")
rows = cursor.fetchall()

def search_wikimedia(query, limit=3):
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",  # File namespace
        "gsrlimit": limit + 5, # Fetch a bit more to filter out svgs
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": 800
    }
    headers = {"User-Agent": "YatraAI-Bot/1.0"}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        
        urls = []
        for page_id, page_data in pages.items():
            if "imageinfo" in page_data:
                info = page_data["imageinfo"][0]
                img_url = info.get("thumburl") or info.get("url")
                if img_url and not img_url.lower().endswith(('.svg', '.pdf', '.ogg', '.webm', '.tif', '.tiff', '.png')):
                    urls.append(img_url)
                    if len(urls) == limit:
                        break
        return urls
    except Exception as e:
        print(f"Error searching wikimedia for {query}: {e}")
        return []

def download_image(url, save_path):
    try:
        res = requests.get(url, timeout=10, headers={"User-Agent": "YatraAI-Bot/1.0"})
        if res.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(res.content)
            return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
    return False

for row in rows:
    attr_id, name, city = row
    print(f"Fetching actual images for {name} ({city})...")
    
    # Precise query for wikimedia
    query = f"{name} {city}"
    if name == "Club Cubana": query = "Nightclub Goa"
    if name == "Bhrigu Lake": query = "Bhrigu Lake"
    if name == "Spice Plantation": query = "Spice plantation Goa"
    
    urls = search_wikimedia(query, 3)
    
    # Fallback to general city if not enough images
    if len(urls) < 1:
        urls = search_wikimedia(city, 3)
        
    safe_name = "".join([c if c.isalnum() else "_" for c in name]).lower()
    saved_urls = []
    
    for i, url in enumerate(urls):
        filename = f"{safe_name}_{i+1}.jpg"
        save_path = os.path.join(images_dir, filename)
        if download_image(url, save_path):
            saved_urls.append(f"/images/{filename}")
            
    if not saved_urls:
        print(f"Could not get any images for {name}")
        continue
        
    # Duplicate if we have less than 3 to ensure array format doesn't break
    while len(saved_urls) < 3:
        saved_urls.append(saved_urls[0])
        
    main_url = saved_urls[0]
    urls_json = json.dumps(saved_urls)
    
    cursor.execute("UPDATE attractions SET image_url = ?, image_urls = ? WHERE id = ?", (main_url, urls_json, attr_id))
    conn.commit()
    print(f"Saved {len(saved_urls)} images for {name}")

conn.close()
print("All images downloaded and database updated successfully!")
