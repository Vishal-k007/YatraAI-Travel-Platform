import sqlite3
import os

DB_PATH = r"c:\Users\Vishal\OneDrive\Desktop\pdd app\backend\travel_platform.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

images = {
    "Beach": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&q=80&w=1000",
    "Heritage": "https://images.unsplash.com/photo-1599661559882-6cb0511874eb?auto=format&fit=crop&q=80&w=1000",
    "Nature": "https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&q=80&w=1000",
    "Shopping": "https://images.unsplash.com/photo-1533900298318-6b8da08a523e?auto=format&fit=crop&q=80&w=1000",
    "Nightlife": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&q=80&w=1000",
    "Culture": "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&q=80&w=1000",
    "Adventure": "https://images.unsplash.com/photo-1522163182402-834f871fd851?auto=format&fit=crop&q=80&w=1000"
}

cursor.execute("SELECT id, name, category FROM attractions")
attractions = cursor.fetchall()
for attr in attractions:
    cat = attr[2]
    url = images.get(cat, "https://images.unsplash.com/photo-1488085061387-422e29b40080?auto=format&fit=crop&q=80&w=1000")
    # A bit of logic for specific places to make them look distinct
    if "Baga" in attr[1]: url = "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&q=80&w=1000"
    if "Amber Fort" in attr[1]: url = "https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&q=80&w=1000"
    if "Hawa Mahal" in attr[1]: url = "https://images.unsplash.com/photo-1599661559882-6cb0511874eb?auto=format&fit=crop&q=80&w=1000"
    if "Solang" in attr[1]: url = "https://images.unsplash.com/photo-1454496522488-7a8e488e8606?auto=format&fit=crop&q=80&w=1000"
    
    cursor.execute("UPDATE attractions SET image_url = ? WHERE id = ?", (url, attr[0]))

conn.commit()
conn.close()
print("Images updated in DB!")
