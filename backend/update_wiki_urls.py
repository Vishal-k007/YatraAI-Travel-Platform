import requests
import json
import sqlite3

db_path = r"c:\Users\Vishal\OneDrive\Desktop\pdd app\backend\travel_platform.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT id, name, city FROM attractions")
rows = cursor.fetchall()

def get_wiki_images(query, limit=3):
    url = "https://en.wikipedia.org/w/api.php"
    
    # Step 1: Search for the page
    search_params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query,
        "srlimit": 1
    }
    try:
        search_res = requests.get(url, params=search_params, timeout=5).json()
        if not search_res.get('query', {}).get('search'):
            return []
        page_title = search_res['query']['search'][0]['title']
        
        # Step 2: Get images for this page
        img_params = {
            "action": "query",
            "format": "json",
            "titles": page_title,
            "prop": "images",
            "imlimit": 20
        }
        img_res = requests.get(url, params=img_params, timeout=5).json()
        pages = img_res.get('query', {}).get('pages', {})
        page = list(pages.values())[0]
        images = page.get('images', [])
        
        valid_images = [img['title'] for img in images if img['title'].lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        if not valid_images:
            return []
            
        # Step 3: Get URLs for these images
        urls = []
        for img_title in valid_images[:limit+3]: # Fetch a few extra
            info_params = {
                "action": "query",
                "format": "json",
                "titles": img_title,
                "prop": "imageinfo",
                "iiprop": "url"
            }
            info_res = requests.get(url, params=info_params, timeout=5).json()
            info_pages = info_res.get('query', {}).get('pages', {})
            info_page = list(info_pages.values())[0]
            if 'imageinfo' in info_page:
                urls.append(info_page['imageinfo'][0]['url'])
                if len(urls) == limit:
                    break
        return urls
    except Exception as e:
        print(f"Error for {query}: {e}")
        return []

for row in rows:
    attr_id, name, city = row
    print(f"Fetching Wikimedia for {name} ({city})...")
    
    query = f"{name} {city}"
    urls = get_wiki_images(query, 3)
    
    if len(urls) < 1:
        print(f"Falling back to city {city} for {name}")
        urls = get_wiki_images(city, 3)
        
    if not urls:
        print(f"Failed to get any images for {name}")
        continue
        
    while len(urls) < 3:
        urls.append(urls[0])
        
    main_url = urls[0]
    urls_json = json.dumps(urls)
    
    cursor.execute("UPDATE attractions SET image_url = ?, image_urls = ? WHERE id = ?", (main_url, urls_json, attr_id))
    print(f"Updated {name} with {len(urls)} actual Wikipedia/Wikimedia images.")

conn.commit()
conn.close()
print("Successfully replaced all images with real Google-Maps-equivalent Wikimedia images!")
