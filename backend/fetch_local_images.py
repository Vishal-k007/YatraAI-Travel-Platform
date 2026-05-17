import os
import time
import requests
from duckduckgo_search import DDGS
import sqlite3
import json

db_path = r"c:\Users\Vishal\OneDrive\Desktop\pdd app\backend\travel_platform.db"
images_dir = r"c:\Users\Vishal\OneDrive\Desktop\pdd app\frontend\public\images"
os.makedirs(images_dir, exist_ok=True)

ddgs = DDGS()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT id, name, city FROM attractions")
rows = cursor.fetchall()

def download_image(url, save_path):
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            if 'text' in content_type or 'html' in content_type:
                return False
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        pass
    return False

for row in rows:
    attr_id, name, city = row
    print(f"Fetching images for {name} ({city})...")
    
    safe_name = "".join([c if c.isalnum() else "_" for c in name]).lower()
    
    results = []
    try:
        results = list(ddgs.images(f"{name} {city} tourist attraction actual photo", max_results=15))
    except Exception as e:
        print(f"Error searching {name}: {e}")
        
    saved_urls = []
    count = 1
    for res in results:
        if count > 3:
            break
        img_url = res.get('image')
        if not img_url: continue
        
        ext = "jpg"
        if img_url.lower().endswith(".png"): ext = "png"
        elif img_url.lower().endswith(".webp"): ext = "webp"
        elif img_url.lower().endswith(".jpeg"): ext = "jpeg"
        
        filename = f"{safe_name}_{count}.{ext}"
        save_path = os.path.join(images_dir, filename)
        
        if download_image(img_url, save_path):
            saved_urls.append(f"/images/{filename}")
            count += 1
            
    if not saved_urls:
        print(f"Could not download any images for {name}.")
        continue
        
    main_url = saved_urls[0]
    urls_json = json.dumps(saved_urls)
    
    cursor.execute("UPDATE attractions SET image_url = ?, image_urls = ? WHERE id = ?", (main_url, urls_json, attr_id))
    conn.commit()
    print(f"Saved {len(saved_urls)} images for {name}.")
    time.sleep(1) # Be nice to DDG

conn.close()
print("All images downloaded and database updated successfully!")
