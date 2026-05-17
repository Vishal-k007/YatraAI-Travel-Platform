import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "travel_platform.db")

REAL_DATA_MAP = {
    # Goa
    "Baga Beach": {
        "image_urls": [
            "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1587595431973-160d0d94add1?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Rahul Desai", "rating": 4.5, "text": "Very crowded but happening. Tito's lane is right there. Great water sports options.", "date": "1 week ago"},
            {"user": "Emily Smith", "rating": 4.0, "text": "Great for sunset. Too many hawkers though, but the shacks serve amazing seafood.", "date": "3 weeks ago"},
            {"user": "Amit Sharma", "rating": 5.0, "text": "Amazing nightlife! The energy here is unmatched in North Goa.", "date": "1 month ago"}
        ],
        "cost_estimate_inr": 1200,
        "cost_breakdown": {"Entry Fee": 0, "Water Sports": 1000, "Transport": 200}
    },
    "Basilica of Bom Jesus": {
        "image_urls": [
            "https://images.unsplash.com/photo-1570051877901-b547849e7943?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1588661642878-5a4ce8c886a1?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1596482163351-4e7cb80dc186?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Priya Singh", "rating": 5.0, "text": "Stunning Portuguese architecture. Very peaceful and historic. A UNESCO world heritage site.", "date": "2 days ago"},
            {"user": "David Brown", "rating": 4.5, "text": "A must-visit for history lovers. The mortal remains of St. Francis Xavier are kept beautifully.", "date": "2 months ago"}
        ],
        "cost_estimate_inr": 200,
        "cost_breakdown": {"Entry Fee": 0, "Donation/Audio Guide": 50, "Transport": 150}
    },
    "Dudhsagar Waterfalls": {
        "image_urls": [
            "https://images.unsplash.com/photo-1593006283731-de8a20235b2e?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1621235334752-959c95111b7f?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1627896157734-4bcbfdfcc022?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Karan V.", "rating": 5.0, "text": "The jeep ride through the jungle is an adventure itself! Breathtaking view of the milk-like water.", "date": "1 week ago"},
            {"user": "Sneha", "rating": 4.0, "text": "Beautiful waterfall, but extremely crowded on weekends. Book the jeep safari early.", "date": "3 weeks ago"}
        ],
        "cost_estimate_inr": 1100,
        "cost_breakdown": {"Jeep Safari": 700, "Entry Fee": 100, "Life Jacket": 100, "Transport": 200}
    },
    "Fort Aguada": {
        "image_urls": [
            "https://images.unsplash.com/photo-1614088515549-011244e883f8?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1614088484179-847d967e88de?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1614088516086-590fb05c879e?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Rohan M.", "rating": 4.0, "text": "Great panoramic views of the Arabian Sea. The lighthouse is iconic.", "date": "1 month ago"},
            {"user": "Neha", "rating": 3.5, "text": "Good place for photos, but gets very hot during the day. Go in the evening.", "date": "2 months ago"}
        ],
        "cost_estimate_inr": 300,
        "cost_breakdown": {"Entry Fee": 50, "Transport": 250}
    },
    "Anjuna Flea Market": {
        "image_urls": [
            "https://images.unsplash.com/photo-1533900298318-6b8da08a523e?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1519014816548-bf5fe059e98b?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1555529771-835f59bfc50c?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Vikram", "rating": 4.5, "text": "Bargaining is a must! You can find unique bohemian stuff here. Held only on Wednesdays.", "date": "1 week ago"},
            {"user": "Alia", "rating": 4.0, "text": "Vibrant and colorful. Live music adds to the great vibe. Don't forget to negotiate hard.", "date": "3 weeks ago"}
        ],
        "cost_estimate_inr": 200,
        "cost_breakdown": {"Entry Fee": 0, "Transport": 200}
    },
    "Club Cubana": {
        "image_urls": [
            "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1566737236500-c8ac43014a67?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1572116469696-ed1f13b632fa?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Kriti", "rating": 5.0, "text": "The Nightclub in the sky! Unlimited drinks with the cover charge. Amazing crowd.", "date": "5 days ago"},
            {"user": "Sam", "rating": 4.5, "text": "Great music across multiple levels. The pool area is the best place to chill between dancing.", "date": "2 weeks ago"}
        ],
        "cost_estimate_inr": 2500,
        "cost_breakdown": {"Cover Charge (Couples)": 2000, "Transport": 500}
    },
    "Palolem Beach": {
        "image_urls": [
            "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1540202404-b711884c7bd4?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1538332576228-eb5b4c4de6f5?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Jenny", "rating": 5.0, "text": "Much cleaner and quieter than North Goa beaches. The crescent shape is beautiful.", "date": "1 month ago"},
            {"user": "Arjun", "rating": 4.5, "text": "Silent noise party on Saturday is a unique experience. Dolphin boat rides are worth it.", "date": "2 months ago"}
        ],
        "cost_estimate_inr": 700,
        "cost_breakdown": {"Entry Fee": 0, "Boat Ride (Dolphin)": 500, "Transport": 200}
    },
    "Spice Plantation": {
        "image_urls": [
            "https://images.unsplash.com/photo-1627896157734-4bcbfdfcc022?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1596649811736-22a0005a81e3?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Meena K.", "rating": 4.5, "text": "Very informative tour about Indian spices. The traditional Goan lunch served on banana leaves was delicious.", "date": "3 weeks ago"},
            {"user": "Saurabh", "rating": 4.0, "text": "A nice break from the beaches. The welcome drink and elephant ride were fun.", "date": "1 month ago"}
        ],
        "cost_estimate_inr": 500,
        "cost_breakdown": {"Entry Tour": 300, "Transport": 200}
    },
    "Chapora Fort": {
        "image_urls": [
            "https://images.unsplash.com/photo-1614088515549-011244e883f8?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1621235334752-959c95111b7f?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1588661642878-5a4ce8c886a1?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Aditi", "rating": 4.5, "text": "Dil Chahta Hai vibes! Best place to watch the sunset overlooking Vagator beach.", "date": "2 weeks ago"},
            {"user": "Rishi", "rating": 4.0, "text": "It's mostly ruins now, but the view is spectacular. Short trek to reach the top.", "date": "1 month ago"}
        ],
        "cost_estimate_inr": 150,
        "cost_breakdown": {"Entry Fee": 0, "Transport": 150}
    },
    "Mangueshi Temple": {
        "image_urls": [
            "https://images.unsplash.com/photo-1596482163351-4e7cb80dc186?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1570051877901-b547849e7943?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1588661642878-5a4ce8c886a1?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Kavita", "rating": 5.0, "text": "Beautiful architecture and very peaceful environment. Dress modestly.", "date": "1 month ago"},
            {"user": "Anil", "rating": 4.5, "text": "Well maintained and very serene. The deepastambha (lamp tower) is very unique.", "date": "2 months ago"}
        ],
        "cost_estimate_inr": 200,
        "cost_breakdown": {"Entry Fee": 0, "Flowers/Offerings": 50, "Transport": 150}
    },

    # Jaipur
    "Amber Fort": {
        "image_urls": [
            "https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1599661559882-6cb0511874eb?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1542898864-1065191c9533?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Aakash", "rating": 5.0, "text": "Stunning architecture! Wear comfortable shoes because there is a lot of walking.", "date": "1 week ago"},
            {"user": "Sarah", "rating": 4.5, "text": "The Sheesh Mahal (Mirror Palace) inside is absolutely breathtaking. Hiring a guide is recommended.", "date": "3 weeks ago"}
        ],
        "cost_estimate_inr": 700,
        "cost_breakdown": {"Entry Fee (Indian)": 100, "Entry (Foreigner)": 500, "Guide": 300, "Transport": 300}
    },
    "Hawa Mahal": {
        "image_urls": [
            "https://images.unsplash.com/photo-1599661559882-6cb0511874eb?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1582510003544-4d00b7f7415e?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1629813580521-1f6b86ab32ea?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Riya", "rating": 4.0, "text": "Best viewed from the cafes opposite the street. Inside is okay, but the facade is the main attraction.", "date": "2 weeks ago"},
            {"user": "John", "rating": 4.5, "text": "Beautiful pink sandstone structure. Great for Instagram photos.", "date": "1 month ago"}
        ],
        "cost_estimate_inr": 100,
        "cost_breakdown": {"Entry Fee": 50, "Transport": 50}
    },
    "City Palace": {
        "image_urls": [
            "https://images.unsplash.com/photo-1542898864-1065191c9533?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1614088515549-011244e883f8?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1582510003544-4d00b7f7415e?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Meera", "rating": 4.5, "text": "A beautiful blend of Rajput and Mughal architecture. The four gates are stunning.", "date": "3 weeks ago"},
            {"user": "Tom", "rating": 4.0, "text": "Very well maintained. The armory and textile museums are highly informative.", "date": "2 months ago"}
        ],
        "cost_estimate_inr": 500,
        "cost_breakdown": {"Entry Fee": 300, "Museum Audio Guide": 200}
    },
    "Jantar Mantar": {
        "image_urls": [
            "https://images.unsplash.com/photo-1599661559882-6cb0511874eb?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1629813580521-1f6b86ab32ea?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Vivek", "rating": 5.0, "text": "Fascinating astronomical instruments. You definitely need a guide to explain how they work.", "date": "1 month ago"},
            {"user": "Elena", "rating": 4.0, "text": "The world's largest stone sundial is mind-boggling.", "date": "2 months ago"}
        ],
        "cost_estimate_inr": 400,
        "cost_breakdown": {"Entry Fee": 50, "Guide (Required for understanding)": 200, "Transport": 150}
    },
    "Johari Bazaar": {
        "image_urls": [
            "https://images.unsplash.com/photo-1533900298318-6b8da08a523e?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1519014816548-bf5fe059e98b?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1555529771-835f59bfc50c?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Simran", "rating": 4.5, "text": "Best place to buy Kundan jewelry and Leheriya sarees. Bargain well!", "date": "1 week ago"},
            {"user": "Neha", "rating": 4.0, "text": "Very crowded but has authentic Rajasthani vibes. Stop for Lassi at LMB.", "date": "3 weeks ago"}
        ],
        "cost_estimate_inr": 200,
        "cost_breakdown": {"Transport": 200}
    },
    "Nahargarh Fort": {
        "image_urls": [
            "https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1599661559882-6cb0511874eb?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1582510003544-4d00b7f7415e?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Rajat", "rating": 5.0, "text": "The sunset view of the entire Jaipur city from here is unparalleled.", "date": "2 weeks ago"},
            {"user": "Pooja", "rating": 4.5, "text": "Padao restaurant at the fort has a cover charge but offers a great evening view.", "date": "1 month ago"}
        ],
        "cost_estimate_inr": 450,
        "cost_breakdown": {"Entry Fee": 50, "Transport (Taxi/Auto)": 400}
    },
    "Albert Hall Museum": {
        "image_urls": [
            "https://images.unsplash.com/photo-1542898864-1065191c9533?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1599661559882-6cb0511874eb?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1629813580521-1f6b86ab32ea?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Aditya", "rating": 4.5, "text": "Looks beautiful at night when lit up! Great collection of artifacts.", "date": "1 week ago"},
            {"user": "Sophie", "rating": 4.0, "text": "Indo-Saracenic architecture is stunning. The Egyptian mummy is a major attraction.", "date": "1 month ago"}
        ],
        "cost_estimate_inr": 190,
        "cost_breakdown": {"Entry Fee": 40, "Transport": 150}
    },
    "Chokhi Dhani": {
        "image_urls": [
            "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1582510003544-4d00b7f7415e?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1555529771-835f59bfc50c?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Vikas", "rating": 4.5, "text": "A complete cultural experience. The traditional Rajasthani thali is very heavy but delicious.", "date": "2 weeks ago"},
            {"user": "Emma", "rating": 4.0, "text": "Fun evening with magic shows, camel rides, and dances. Slightly expensive but worth a one-time visit.", "date": "3 weeks ago"}
        ],
        "cost_estimate_inr": 800,
        "cost_breakdown": {"Entry Ticket": 700, "Transport": 500, "Activities": 100}
    },
    "Galtaji Temple (Monkey Temple)": {
        "image_urls": [
            "https://images.unsplash.com/photo-1599661559882-6cb0511874eb?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1542898864-1065191c9533?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Nitin", "rating": 4.0, "text": "Very ancient and mystical place. Lots of monkeys, so hold onto your belongings.", "date": "1 month ago"},
            {"user": "Clara", "rating": 4.5, "text": "The holy water pools and the temple nestled in the hills offer a very spiritual vibe.", "date": "2 months ago"}
        ],
        "cost_estimate_inr": 250,
        "cost_breakdown": {"Entry Fee": 0, "Camera Fee": 50, "Transport": 200}
    },
    "Bapu Bazaar": {
        "image_urls": [
            "https://images.unsplash.com/photo-1533900298318-6b8da08a523e?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1519014816548-bf5fe059e98b?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1555529771-835f59bfc50c?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Shikha", "rating": 4.5, "text": "Excellent place to buy Mojaris (traditional shoes) and Jaipuri bedsheets.", "date": "2 weeks ago"},
            {"user": "Ravi", "rating": 4.0, "text": "Great street shopping experience. The pink buildings look beautiful. Remember to bargain.", "date": "3 weeks ago"}
        ],
        "cost_estimate_inr": 100,
        "cost_breakdown": {"Transport": 100}
    },

    # Manali
    "Solang Valley": {
        "image_urls": [
            "https://images.unsplash.com/photo-1454496522488-7a8e488e8606?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1522163182402-834f871fd851?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Nikhil", "rating": 5.0, "text": "The adventure hub of Manali! Paragliding was an unforgettable experience.", "date": "1 week ago"},
            {"user": "Pooja", "rating": 4.0, "text": "Gets very crowded in peak season. Traffic jam on the way is common, start early.", "date": "3 weeks ago"}
        ],
        "cost_estimate_inr": 3300,
        "cost_breakdown": {"Paragliding/Skiing": 2000, "ATV Ride": 500, "Winter Clothes Rent": 500, "Transport": 300}
    },
    "Hadimba Devi Temple": {
        "image_urls": [
            "https://images.unsplash.com/photo-1599661559882-6cb0511874eb?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1542898864-1065191c9533?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Amit", "rating": 4.5, "text": "Very serene temple surrounded by tall cedar trees. Unique wooden architecture.", "date": "2 weeks ago"},
            {"user": "Chloe", "rating": 4.0, "text": "Peaceful atmosphere. Be careful of the aggressive locals selling photos with rabbits/yaks.", "date": "1 month ago"}
        ],
        "cost_estimate_inr": 150,
        "cost_breakdown": {"Entry Fee": 0, "Yaks/Photo op": 100, "Transport": 50}
    },
    "Rohtang Pass": {
        "image_urls": [
            "https://images.unsplash.com/photo-1454496522488-7a8e488e8606?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1522163182402-834f871fd851?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Gaurav", "rating": 5.0, "text": "Absolute heaven! Playing in the snow at 13000 ft was incredible. Spectacular views.", "date": "1 week ago"},
            {"user": "Neha", "rating": 4.0, "text": "Need to book permits well in advance. The journey is scary but beautiful.", "date": "2 months ago"}
        ],
        "cost_estimate_inr": 2000,
        "cost_breakdown": {"Permit & Transport (Shared Taxi)": 1500, "Snow Dress Rent": 500}
    },
    "Old Manali": {
        "image_urls": [
            "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1519014816548-bf5fe059e98b?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1533900298318-6b8da08a523e?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Varun", "rating": 5.0, "text": "The hipster capital! Great live music cafes, bakeries, and cheap hippie clothes.", "date": "2 weeks ago"},
            {"user": "Jessica", "rating": 4.5, "text": "Much better vibe than the main Mall road. Dylan's Toasted & Roasted coffee is a must.", "date": "1 month ago"}
        ],
        "cost_estimate_inr": 100,
        "cost_breakdown": {"Transport (Tuk-tuk)": 100}
    },
    "Vashisht Hot Water Springs": {
        "image_urls": [
            "https://images.unsplash.com/photo-1599661559882-6cb0511874eb?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Manish", "rating": 4.0, "text": "Taking a dip in the natural hot springs is very relaxing, especially in cold weather.", "date": "3 weeks ago"},
            {"user": "Lisa", "rating": 3.5, "text": "The water is great but the changing rooms could be cleaner. The temple is nice.", "date": "1 month ago"}
        ],
        "cost_estimate_inr": 100,
        "cost_breakdown": {"Entry Fee": 0, "Transport": 100}
    },
    "Jogini Waterfall": {
        "image_urls": [
            "https://images.unsplash.com/photo-1627896157734-4bcbfdfcc022?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1593006283731-de8a20235b2e?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Aryan", "rating": 5.0, "text": "A beautiful 1-hour trek from Vashisht. The waterfall is massive and secluded.", "date": "2 weeks ago"},
            {"user": "Geeta", "rating": 4.5, "text": "Very pristine and peaceful. Best to carry your own water bottle and snacks.", "date": "1 month ago"}
        ],
        "cost_estimate_inr": 100,
        "cost_breakdown": {"Entry Fee": 0, "Transport to Vashisht": 100}
    },
    "Manikaran Sahib": {
        "image_urls": [
            "https://images.unsplash.com/photo-1599661559882-6cb0511874eb?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1542898864-1065191c9533?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Ramesh", "rating": 5.0, "text": "Very spiritual place. The hot springs are boiling, and the langar food is amazing.", "date": "1 week ago"},
            {"user": "Sunita", "rating": 4.5, "text": "Beautiful location in the Parvati valley. The hot caves are a unique experience.", "date": "3 weeks ago"}
        ],
        "cost_estimate_inr": 500,
        "cost_breakdown": {"Entry Fee": 0, "Donation/Langar": 100, "Transport from Manali (Bus/Taxi)": 400}
    },
    "Mall Road": {
        "image_urls": [
            "https://images.unsplash.com/photo-1519014816548-bf5fe059e98b?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1533900298318-6b8da08a523e?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Deepak", "rating": 4.0, "text": "Good for evening strolls and buying local souvenirs. Try the softy ice cream!", "date": "2 weeks ago"},
            {"user": "Maria", "rating": 4.5, "text": "Very busy, but has all the restaurants and shops you need. Great winter wear options.", "date": "1 month ago"}
        ],
        "cost_estimate_inr": 100,
        "cost_breakdown": {"Transport": 100}
    },
    "Bhrigu Lake": {
        "image_urls": [
            "https://images.unsplash.com/photo-1454496522488-7a8e488e8606?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1522163182402-834f871fd851?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Trekker_Raj", "rating": 5.0, "text": "An arduous but absolutely rewarding trek. The high altitude meadows and the lake are pristine.", "date": "1 month ago"},
            {"user": "Jason", "rating": 4.5, "text": "Requires good fitness. The views of the Pir Panjal range are breathtaking.", "date": "2 months ago"}
        ],
        "cost_estimate_inr": 2000,
        "cost_breakdown": {"Trek Guide/Package": 1500, "Transport to Base": 500}
    },
    "Naggar Castle": {
        "image_urls": [
            "https://images.unsplash.com/photo-1542898864-1065191c9533?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1599661559882-6cb0511874eb?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1582510003544-4d00b7f7415e?auto=format&fit=crop&w=800&q=80"
        ],
        "reviews": [
            {"user": "Kabir", "rating": 4.5, "text": "Beautiful wooden architecture. Made famous by the movie Jab We Met. Excellent valley views.", "date": "3 weeks ago"},
            {"user": "Sonia", "rating": 4.0, "text": "Very quaint and historic. The Roerich Art Gallery nearby is also a must-visit.", "date": "1 month ago"}
        ],
        "cost_estimate_inr": 230,
        "cost_breakdown": {"Entry Fee": 30, "Transport": 200}
    },
}

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM attractions")
    rows = cursor.fetchall()
    print(f"Found {len(rows)} attractions in DB.")

    for row in rows:
        attr_id = row[0]
        name = row[1]

        if name in REAL_DATA_MAP:
            data = REAL_DATA_MAP[name]
            image_urls_json = json.dumps(data["image_urls"])
            reviews_json = json.dumps(data["reviews"])
            cost_breakdown_json = json.dumps(data["cost_breakdown"])
            cost_estimate = data["cost_estimate_inr"]
            main_image_url = data["image_urls"][0]

            cursor.execute("""
                UPDATE attractions 
                SET image_url = ?, image_urls = ?, reviews = ?, cost_breakdown = ?, cost_estimate_inr = ?
                WHERE id = ?
            """, (main_image_url, image_urls_json, reviews_json, cost_breakdown_json, cost_estimate, attr_id))
            print(f"Updated: {name}")
        else:
            print(f"Skipped (Not in REAL_DATA_MAP): {name}")

    conn.commit()
    conn.close()
    print("Database successfully updated with actual realistic Google Maps simulation data!")

if __name__ == "__main__":
    main()
