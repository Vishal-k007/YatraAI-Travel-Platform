"""
Seed data script to populate the database with attractions.
Contains ~60 real attractions across Goa, Jaipur, and Manali.
"""
import json
import os
from models import Attraction, User, TravelerProfile
from auth import hash_password

# Helper to generate random recommended archetypes
def get_archetypes(primary, *others):
    archetypes = [primary] + list(others)
    return archetypes

def enrich_attraction_data(attr_data):
    # 1. Place images from curated map (run apply_curated_images.py after seeding)
    curated_path = os.path.join(os.path.dirname(__file__), "place_images_curated.json")
    image_set = False
    if os.path.exists(curated_path):
        with open(curated_path, encoding="utf-8") as f:
            curated = json.load(f)
        urls = curated.get(attr_data["name"])
        if urls:
            from urllib.parse import urlparse, urlunparse
            clean = [urlunparse(urlparse(u)._replace(query="", fragment="")) for u in urls[:3]]
            while len(clean) < 3:
                clean.append(clean[0])
            attr_data["image_urls"] = clean
            attr_data["image_url"] = clean[0]
            image_set = True
    if not image_set:
        image_seed = attr_data['name'].replace(' ', '')
        image_urls = [
            f"https://picsum.photos/seed/{image_seed}1/800/600",
            f"https://picsum.photos/seed/{image_seed}2/800/600",
            f"https://picsum.photos/seed/{image_seed}3/800/600",
        ]
        attr_data["image_urls"] = image_urls
        attr_data["image_url"] = image_urls[0]

    # 2. Real-time Reviews
    names = ["Rahul", "Priya", "Amit", "Sneha", "Karan", "Anjali", "Vikram", "Riya", "Rohan", "Neha", "Aditya", "Pooja"]
    positive_comments = [
        "Absolutely amazing experience! The vibe was fantastic.",
        "A must-visit if you're in the city. Truly breathtaking.",
        "Loved the atmosphere and the views. Highly recommended.",
        "Great place to spend time with family and friends. Worth every penny.",
        "The architecture and history here is just mind-blowing.",
        "One of the best spots! Don't miss this.",
        "A bit crowded during peak hours, but still very enjoyable.",
        "Perfect place for photography. Got some amazing shots!",
        "The local food nearby is incredibly delicious.",
        "Such a peaceful and serene environment. Will definitely come back."
    ]
    num_reviews = random.randint(3, 7)
    reviews = []
    for _ in range(num_reviews):
        days_ago = random.randint(1, 14)
        review_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        reviews.append({
            "user": random.choice(names),
            "rating": random.choice([4, 4.5, 5]),
            "text": random.choice(positive_comments),
            "date": review_date
        })
    # Sort reviews by date descending (simulating real-time recent reviews)
    reviews.sort(key=lambda x: x["date"], reverse=True)
    attr_data["reviews"] = reviews
    
    # 3. Realistic Cost Breakdown
    base_cost = attr_data.get("cost_estimate_inr", 0)
    if base_cost == 0:
        attr_data["cost_breakdown"] = {"Entry Fee": "Free", "Transport": 150, "Food & Snacks": 350}
        attr_data["cost_estimate_inr"] = 500  # realistic total cost
    else:
        # Provide a more realistic breakdown for paid attractions
        transport = int(base_cost * 0.2)
        food = int(base_cost * 0.4)
        entry_or_activity = base_cost - transport - food
        attr_data["cost_breakdown"] = {
            "Entry/Activity Fee": entry_or_activity,
            "Transport": transport,
            "Food & Drinks": food
        }
        
    return attr_data

# --- Goa Attractions ---
GOA_ATTRACTIONS = [
    {
        "name": "Baga Beach", "city": "Goa", "category": "Beach",
        "description": "One of the most famous beaches in Goa, known for its vibrant nightlife, water sports, and beach shacks.",
        "latitude": 15.5553, "longitude": 73.7517, "avg_visit_duration_hours": 4.0, "cost_estimate_inr": 1500,
        "best_visiting_time": "Evening", "crowd_density": 5.0, "physical_intensity": 2.0, "photography_score": 4.0,
        "food_availability": 5.0, "family_friendliness": 3.0, "adventure_level": 4.0, "cultural_depth": 1.0,
        "nightlife_score": 5.0, "weather_sensitivity": 5.0, "is_indoor": False,
        "recommended_archetypes": get_archetypes("High-Energy Social Explorer", "Adventure-Focused Wanderer")
    },
    {
        "name": "Basilica of Bom Jesus", "city": "Goa", "category": "Heritage",
        "description": "UNESCO World Heritage site containing the mortal remains of St. Francis Xavier.",
        "latitude": 15.5009, "longitude": 73.9116, "avg_visit_duration_hours": 1.5, "cost_estimate_inr": 0,
        "best_visiting_time": "Morning", "crowd_density": 4.0, "physical_intensity": 1.0, "photography_score": 5.0,
        "food_availability": 2.0, "family_friendliness": 4.0, "adventure_level": 1.0, "cultural_depth": 5.0,
        "nightlife_score": 1.0, "weather_sensitivity": 2.0, "is_indoor": True,
        "recommended_archetypes": get_archetypes("Cultural Depth Traveler", "Comfort-Oriented Relaxer")
    },
    {
        "name": "Dudhsagar Waterfalls", "city": "Goa", "category": "Nature",
        "description": "Majestic four-tiered waterfall on the Mandovi River, best visited after monsoon.",
        "latitude": 15.3144, "longitude": 74.3143, "avg_visit_duration_hours": 5.0, "cost_estimate_inr": 1000,
        "best_visiting_time": "Morning", "crowd_density": 3.0, "physical_intensity": 4.0, "photography_score": 5.0,
        "food_availability": 1.0, "family_friendliness": 2.0, "adventure_level": 5.0, "cultural_depth": 1.0,
        "nightlife_score": 1.0, "weather_sensitivity": 5.0, "is_indoor": False,
        "recommended_archetypes": get_archetypes("Adventure-Focused Wanderer", "Budget Nature Seeker")
    },
    {
        "name": "Fort Aguada", "city": "Goa", "category": "Heritage",
        "description": "17th-century Portuguese fort standing on Sinquerim Beach overlooking the Arabian Sea.",
        "latitude": 15.4988, "longitude": 73.7686, "avg_visit_duration_hours": 2.0, "cost_estimate_inr": 300,
        "best_visiting_time": "Afternoon", "crowd_density": 4.0, "physical_intensity": 3.0, "photography_score": 5.0,
        "food_availability": 2.0, "family_friendliness": 4.0, "adventure_level": 2.0, "cultural_depth": 4.0,
        "nightlife_score": 1.0, "weather_sensitivity": 4.0, "is_indoor": False,
        "recommended_archetypes": get_archetypes("Cultural Depth Traveler", "High-Energy Social Explorer")
    },
    {
        "name": "Anjuna Flea Market", "city": "Goa", "category": "Shopping",
        "description": "Iconic Wednesday market offering clothes, jewelry, souvenirs, and live music.",
        "latitude": 15.5804, "longitude": 73.7444, "avg_visit_duration_hours": 3.0, "cost_estimate_inr": 2000,
        "best_visiting_time": "Evening", "crowd_density": 5.0, "physical_intensity": 3.0, "photography_score": 4.0,
        "food_availability": 4.0, "family_friendliness": 3.0, "adventure_level": 1.0, "cultural_depth": 3.0,
        "nightlife_score": 3.0, "weather_sensitivity": 4.0, "is_indoor": False,
        "recommended_archetypes": get_archetypes("High-Energy Social Explorer", "Cultural Depth Traveler")
    },
    {
        "name": "Club Cubana", "city": "Goa", "category": "Nightlife",
        "description": "Neon-lit nightclub set on a hill with a pool and multi-level dance floors.",
        "latitude": 15.5800, "longitude": 73.7663, "avg_visit_duration_hours": 4.0, "cost_estimate_inr": 3000,
        "best_visiting_time": "Night", "crowd_density": 5.0, "physical_intensity": 4.0, "photography_score": 3.0,
        "food_availability": 4.0, "family_friendliness": 1.0, "adventure_level": 1.0, "cultural_depth": 1.0,
        "nightlife_score": 5.0, "weather_sensitivity": 2.0, "is_indoor": True,
        "recommended_archetypes": get_archetypes("High-Energy Social Explorer")
    },
    {
        "name": "Palolem Beach", "city": "Goa", "category": "Beach",
        "description": "Crescent-shaped beach in South Goa known for calm waters and silent discos.",
        "latitude": 15.0100, "longitude": 74.0232, "avg_visit_duration_hours": 5.0, "cost_estimate_inr": 1200,
        "best_visiting_time": "Any", "crowd_density": 3.0, "physical_intensity": 1.0, "photography_score": 5.0,
        "food_availability": 4.0, "family_friendliness": 5.0, "adventure_level": 2.0, "cultural_depth": 2.0,
        "nightlife_score": 4.0, "weather_sensitivity": 5.0, "is_indoor": False,
        "recommended_archetypes": get_archetypes("Comfort-Oriented Relaxer", "Budget Nature Seeker")
    },
    {
        "name": "Spice Plantation", "city": "Goa", "category": "Nature",
        "description": "Guided tours through lush plantations learning about Indian spices, with traditional lunch.",
        "latitude": 15.3995, "longitude": 74.0205, "avg_visit_duration_hours": 3.0, "cost_estimate_inr": 800,
        "best_visiting_time": "Morning", "crowd_density": 2.0, "physical_intensity": 2.0, "photography_score": 4.0,
        "food_availability": 5.0, "family_friendliness": 5.0, "adventure_level": 1.0, "cultural_depth": 4.0,
        "nightlife_score": 1.0, "weather_sensitivity": 3.0, "is_indoor": False,
        "recommended_archetypes": get_archetypes("Cultural Depth Traveler", "Budget Nature Seeker")
    },
    {
        "name": "Chapora Fort", "city": "Goa", "category": "Heritage",
        "description": "Ruined fort made famous by Bollywood movies, offering spectacular sunset views over Vagator beach.",
        "latitude": 15.6060, "longitude": 73.7360, "avg_visit_duration_hours": 1.5, "cost_estimate_inr": 0,
        "best_visiting_time": "Evening", "crowd_density": 4.0, "physical_intensity": 3.0, "photography_score": 5.0,
        "food_availability": 1.0, "family_friendliness": 3.0, "adventure_level": 2.0, "cultural_depth": 3.0,
        "nightlife_score": 1.0, "weather_sensitivity": 4.0, "is_indoor": False,
        "recommended_archetypes": get_archetypes("Budget Nature Seeker", "High-Energy Social Explorer")
    },
    {
        "name": "Mangueshi Temple", "city": "Goa", "category": "Heritage",
        "description": "Prominent Hindu temple dedicated to Lord Shiva, known for its distinct Goan architecture.",
        "latitude": 15.4385, "longitude": 73.9678, "avg_visit_duration_hours": 1.0, "cost_estimate_inr": 0,
        "best_visiting_time": "Morning", "crowd_density": 3.0, "physical_intensity": 1.0, "photography_score": 4.0,
        "food_availability": 1.0, "family_friendliness": 5.0, "adventure_level": 1.0, "cultural_depth": 5.0,
        "nightlife_score": 1.0, "weather_sensitivity": 2.0, "is_indoor": True,
        "recommended_archetypes": get_archetypes("Cultural Depth Traveler", "Comfort-Oriented Relaxer")
    }
]

# --- Jaipur Attractions ---
JAIPUR_ATTRACTIONS = [
    {
        "name": "Amber Fort", "city": "Jaipur", "category": "Heritage",
        "description": "Majestic hilltop fort known for its artistic Hindu style elements, massive ramparts, and cobbled paths.",
        "latitude": 26.9855, "longitude": 75.8513, "avg_visit_duration_hours": 3.0, "cost_estimate_inr": 500,
        "best_visiting_time": "Morning", "crowd_density": 5.0, "physical_intensity": 4.0, "photography_score": 5.0,
        "food_availability": 3.0, "family_friendliness": 4.0, "adventure_level": 2.0, "cultural_depth": 5.0,
        "nightlife_score": 1.0, "weather_sensitivity": 4.0, "is_indoor": False,
        "recommended_archetypes": get_archetypes("Cultural Depth Traveler", "High-Energy Social Explorer")
    },
    {
        "name": "Hawa Mahal", "city": "Jaipur", "category": "Heritage",
        "description": "The 'Palace of Winds', a five-story building with 953 small windows decorated with intricate latticework.",
        "latitude": 26.9239, "longitude": 75.8267, "avg_visit_duration_hours": 1.0, "cost_estimate_inr": 200,
        "best_visiting_time": "Morning", "crowd_density": 5.0, "physical_intensity": 2.0, "photography_score": 5.0,
        "food_availability": 4.0, "family_friendliness": 5.0, "adventure_level": 1.0, "cultural_depth": 5.0,
        "nightlife_score": 1.0, "weather_sensitivity": 2.0, "is_indoor": False,
        "recommended_archetypes": get_archetypes("Cultural Depth Traveler", "Comfort-Oriented Relaxer")
    },
    {
        "name": "City Palace", "city": "Jaipur", "category": "Heritage",
        "description": "A complex of courtyards, gardens and buildings right in the center of the Old City.",
        "latitude": 26.9255, "longitude": 75.8236, "avg_visit_duration_hours": 2.5, "cost_estimate_inr": 700,
        "best_visiting_time": "Afternoon", "crowd_density": 4.0, "physical_intensity": 2.0, "photography_score": 5.0,
        "food_availability": 3.0, "family_friendliness": 5.0, "adventure_level": 1.0, "cultural_depth": 5.0,
        "nightlife_score": 1.0, "weather_sensitivity": 2.0, "is_indoor": True,
        "recommended_archetypes": get_archetypes("Comfort-Oriented Relaxer", "Cultural Depth Traveler")
    },
    {
        "name": "Jantar Mantar", "city": "Jaipur", "category": "Heritage",
        "description": "Astronomical observation site built in the 18th century, featuring the world's largest stone sundial.",
        "latitude": 26.9248, "longitude": 75.8246, "avg_visit_duration_hours": 1.5, "cost_estimate_inr": 200,
        "best_visiting_time": "Morning", "crowd_density": 4.0, "physical_intensity": 2.0, "photography_score": 4.0,
        "food_availability": 2.0, "family_friendliness": 5.0, "adventure_level": 1.0, "cultural_depth": 5.0,
        "nightlife_score": 1.0, "weather_sensitivity": 5.0, "is_indoor": False,
        "recommended_archetypes": get_archetypes("Cultural Depth Traveler", "Comfort-Oriented Relaxer")
    },
    {
        "name": "Johari Bazaar", "city": "Jaipur", "category": "Shopping",
        "description": "Vibrant market famous for traditional Rajasthani jewelry, gems, and textiles.",
        "latitude": 26.9196, "longitude": 75.8266, "avg_visit_duration_hours": 3.0, "cost_estimate_inr": 5000,
        "best_visiting_time": "Evening", "crowd_density": 5.0, "physical_intensity": 3.0, "photography_score": 4.0,
        "food_availability": 5.0, "family_friendliness": 3.0, "adventure_level": 1.0, "cultural_depth": 4.0,
        "nightlife_score": 2.0, "weather_sensitivity": 3.0, "is_indoor": False,
        "recommended_archetypes": get_archetypes("High-Energy Social Explorer", "Cultural Depth Traveler")
    },
    {
        "name": "Nahargarh Fort", "city": "Jaipur", "category": "Heritage",
        "description": "Fort situated on the Aravalli hills overlooking the pink city of Jaipur, great for sunsets.",
        "latitude": 26.9372, "longitude": 75.8155, "avg_visit_duration_hours": 2.5, "cost_estimate_inr": 200,
        "best_visiting_time": "Evening", "crowd_density": 4.0, "physical_intensity": 3.0, "photography_score": 5.0,
        "food_availability": 4.0, "family_friendliness": 4.0, "adventure_level": 2.0, "cultural_depth": 4.0,
        "nightlife_score": 2.0, "weather_sensitivity": 4.0, "is_indoor": False,
        "recommended_archetypes": get_archetypes("High-Energy Social Explorer", "Budget Nature Seeker")
    },
    {
        "name": "Albert Hall Museum", "city": "Jaipur", "category": "Heritage",
        "description": "The oldest museum of the state, functioning as the State museum of Rajasthan.",
        "latitude": 26.9116, "longitude": 75.8195, "avg_visit_duration_hours": 2.0, "cost_estimate_inr": 300,
        "best_visiting_time": "Afternoon", "crowd_density": 3.0, "physical_intensity": 1.0, "photography_score": 4.0,
        "food_availability": 2.0, "family_friendliness": 4.0, "adventure_level": 1.0, "cultural_depth": 5.0,
        "nightlife_score": 1.0, "weather_sensitivity": 1.0, "is_indoor": True,
        "recommended_archetypes": get_archetypes("Cultural Depth Traveler", "Comfort-Oriented Relaxer")
    },
    {
        "name": "Chokhi Dhani", "city": "Jaipur", "category": "Culture",
        "description": "A mock Rajasthani village offering traditional food, cultural performances, and activities.",
        "latitude": 26.7667, "longitude": 75.8252, "avg_visit_duration_hours": 4.0, "cost_estimate_inr": 1500,
        "best_visiting_time": "Night", "crowd_density": 5.0, "physical_intensity": 2.0, "photography_score": 4.0,
        "food_availability": 5.0, "family_friendliness": 5.0, "adventure_level": 1.0, "cultural_depth": 4.0,
        "nightlife_score": 3.0, "weather_sensitivity": 3.0, "is_indoor": False,
        "recommended_archetypes": get_archetypes("Comfort-Oriented Relaxer", "Cultural Depth Traveler")
    },
    {
        "name": "Galtaji Temple (Monkey Temple)", "city": "Jaipur", "category": "Heritage",
        "description": "Ancient Hindu pilgrimage site consisting of a series of temples built into a narrow crevice in the hills.",
        "latitude": 26.9168, "longitude": 75.8587, "avg_visit_duration_hours": 2.0, "cost_estimate_inr": 100,
        "best_visiting_time": "Morning", "crowd_density": 3.0, "physical_intensity": 3.0, "photography_score": 5.0,
        "food_availability": 1.0, "family_friendliness": 3.0, "adventure_level": 2.0, "cultural_depth": 5.0,
        "nightlife_score": 1.0, "weather_sensitivity": 4.0, "is_indoor": False,
        "recommended_archetypes": get_archetypes("Cultural Depth Traveler", "Adventure-Focused Wanderer")
    },
    {
        "name": "Bapu Bazaar", "city": "Jaipur", "category": "Shopping",
        "description": "Bustling market known for camel leather items, particularly traditional Mojari footwear.",
        "latitude": 26.9185, "longitude": 75.8234, "avg_visit_duration_hours": 2.0, "cost_estimate_inr": 2000,
        "best_visiting_time": "Evening", "crowd_density": 5.0, "physical_intensity": 3.0, "photography_score": 3.0,
        "food_availability": 4.0, "family_friendliness": 3.0, "adventure_level": 1.0, "cultural_depth": 3.0,
        "nightlife_score": 1.0, "weather_sensitivity": 3.0, "is_indoor": False,
        "recommended_archetypes": get_archetypes("High-Energy Social Explorer", "Cultural Depth Traveler")
    }
]

# --- Manali Attractions ---
MANALI_ATTRACTIONS = [
    {
        "name": "Solang Valley", "city": "Manali", "category": "Adventure",
        "description": "A picturesque valley known for its summer and winter sport conditions, especially skiing and paragliding.",
        "latitude": 32.3169, "longitude": 77.1581, "avg_visit_duration_hours": 4.0, "cost_estimate_inr": 3000,
        "best_visiting_time": "Morning", "crowd_density": 5.0, "physical_intensity": 4.0, "photography_score": 5.0,
        "food_availability": 3.0, "family_friendliness": 4.0, "adventure_level": 5.0, "cultural_depth": 1.0,
        "nightlife_score": 1.0, "weather_sensitivity": 5.0, "is_indoor": False,
        "recommended_archetypes": get_archetypes("Adventure-Focused Wanderer", "High-Energy Social Explorer")
    },
    {
        "name": "Hadimba Devi Temple", "city": "Manali", "category": "Heritage",
        "description": "Ancient cave temple dedicated to Hidimbi Devi, surrounded by a cedar forest.",
        "latitude": 32.2464, "longitude": 77.1824, "avg_visit_duration_hours": 1.0, "cost_estimate_inr": 0,
        "best_visiting_time": "Morning", "crowd_density": 4.0, "physical_intensity": 1.0, "photography_score": 4.0,
        "food_availability": 2.0, "family_friendliness": 5.0, "adventure_level": 1.0, "cultural_depth": 4.0,
        "nightlife_score": 1.0, "weather_sensitivity": 3.0, "is_indoor": False,
        "recommended_archetypes": get_archetypes("Cultural Depth Traveler", "Comfort-Oriented Relaxer")
    },
    {
        "name": "Rohtang Pass", "city": "Manali", "category": "Nature",
        "description": "High mountain pass on the eastern Pir Panjal Range connecting Kullu Valley with Lahaul and Spiti.",
        "latitude": 32.3716, "longitude": 77.2466, "avg_visit_duration_hours": 6.0, "cost_estimate_inr": 4000,
        "best_visiting_time": "Morning", "crowd_density": 5.0, "physical_intensity": 3.0, "photography_score": 5.0,
        "food_availability": 2.0, "family_friendliness": 3.0, "adventure_level": 4.0, "cultural_depth": 1.0,
        "nightlife_score": 1.0, "weather_sensitivity": 5.0, "is_indoor": False,
        "recommended_archetypes": get_archetypes("Adventure-Focused Wanderer", "Budget Nature Seeker")
    },
    {
        "name": "Old Manali", "city": "Manali", "category": "Culture",
        "description": "Quaint area with traditional houses, backpacker cafes, and artisan shops.",
        "latitude": 32.2530, "longitude": 77.1818, "avg_visit_duration_hours": 3.0, "cost_estimate_inr": 1500,
        "best_visiting_time": "Evening", "crowd_density": 3.0, "physical_intensity": 2.0, "photography_score": 4.0,
        "food_availability": 5.0, "family_friendliness": 3.0, "adventure_level": 1.0, "cultural_depth": 3.0,
        "nightlife_score": 4.0, "weather_sensitivity": 3.0, "is_indoor": False,
        "recommended_archetypes": get_archetypes("High-Energy Social Explorer", "Cultural Depth Traveler")
    },
    {
        "name": "Vashisht Hot Water Springs", "city": "Manali", "category": "Nature",
        "description": "Natural hot sulfur springs with therapeutic properties, located near the Vashisht Temple.",
        "latitude": 32.2618, "longitude": 77.1956, "avg_visit_duration_hours": 2.0, "cost_estimate_inr": 100,
        "best_visiting_time": "Morning", "crowd_density": 4.0, "physical_intensity": 2.0, "photography_score": 3.0,
        "food_availability": 2.0, "family_friendliness": 4.0, "adventure_level": 1.0, "cultural_depth": 4.0,
        "nightlife_score": 1.0, "weather_sensitivity": 2.0, "is_indoor": True,
        "recommended_archetypes": get_archetypes("Comfort-Oriented Relaxer", "Cultural Depth Traveler")
    },
    {
        "name": "Jogini Waterfall", "city": "Manali", "category": "Nature",
        "description": "Scenic waterfall accessible via a short trek through pine forests and apple orchards.",
        "latitude": 32.2778, "longitude": 77.1887, "avg_visit_duration_hours": 3.0, "cost_estimate_inr": 0,
        "best_visiting_time": "Afternoon", "crowd_density": 2.0, "physical_intensity": 4.0, "photography_score": 5.0,
        "food_availability": 1.0, "family_friendliness": 2.0, "adventure_level": 3.0, "cultural_depth": 1.0,
        "nightlife_score": 1.0, "weather_sensitivity": 4.0, "is_indoor": False,
        "recommended_archetypes": get_archetypes("Budget Nature Seeker", "Adventure-Focused Wanderer")
    },
    {
        "name": "Manikaran Sahib", "city": "Manali", "category": "Heritage",
        "description": "Prominent Sikh pilgrimage center known for its hot springs and langar (community kitchen).",
        "latitude": 32.0272, "longitude": 77.3468, "avg_visit_duration_hours": 4.0, "cost_estimate_inr": 200,
        "best_visiting_time": "Morning", "crowd_density": 4.0, "physical_intensity": 2.0, "photography_score": 4.0,
        "food_availability": 4.0, "family_friendliness": 5.0, "adventure_level": 1.0, "cultural_depth": 5.0,
        "nightlife_score": 1.0, "weather_sensitivity": 3.0, "is_indoor": False,
        "recommended_archetypes": get_archetypes("Cultural Depth Traveler", "Comfort-Oriented Relaxer")
    },
    {
        "name": "Mall Road", "city": "Manali", "category": "Shopping",
        "description": "The main street in Manali, lined with hotels, restaurants, shops, and cafes.",
        "latitude": 32.2432, "longitude": 77.1892, "avg_visit_duration_hours": 2.5, "cost_estimate_inr": 2000,
        "best_visiting_time": "Evening", "crowd_density": 5.0, "physical_intensity": 2.0, "photography_score": 3.0,
        "food_availability": 5.0, "family_friendliness": 5.0, "adventure_level": 1.0, "cultural_depth": 2.0,
        "nightlife_score": 3.0, "weather_sensitivity": 4.0, "is_indoor": False,
        "recommended_archetypes": get_archetypes("Comfort-Oriented Relaxer", "High-Energy Social Explorer")
    },
    {
        "name": "Bhrigu Lake", "city": "Manali", "category": "Adventure",
        "description": "High altitude glacial lake offering spectacular views of the Pir Panjal range.",
        "latitude": 32.3023, "longitude": 77.2345, "avg_visit_duration_hours": 8.0, "cost_estimate_inr": 1500,
        "best_visiting_time": "Morning", "crowd_density": 1.0, "physical_intensity": 5.0, "photography_score": 5.0,
        "food_availability": 1.0, "family_friendliness": 1.0, "adventure_level": 5.0, "cultural_depth": 2.0,
        "nightlife_score": 1.0, "weather_sensitivity": 5.0, "is_indoor": False,
        "recommended_archetypes": get_archetypes("Adventure-Focused Wanderer", "Budget Nature Seeker")
    },
    {
        "name": "Naggar Castle", "city": "Manali", "category": "Heritage",
        "description": "Historic castle made of wood and stone, offering panoramic views of the Kullu Valley.",
        "latitude": 32.1158, "longitude": 77.1706, "avg_visit_duration_hours": 2.0, "cost_estimate_inr": 100,
        "best_visiting_time": "Afternoon", "crowd_density": 2.0, "physical_intensity": 1.0, "photography_score": 5.0,
        "food_availability": 3.0, "family_friendliness": 5.0, "adventure_level": 1.0, "cultural_depth": 5.0,
        "nightlife_score": 1.0, "weather_sensitivity": 2.0, "is_indoor": True,
        "recommended_archetypes": get_archetypes("Cultural Depth Traveler", "Comfort-Oriented Relaxer")
    }
]

ALL_ATTRACTIONS = GOA_ATTRACTIONS + JAIPUR_ATTRACTIONS + MANALI_ATTRACTIONS

def seed_database(db_session):
    """Inserts seed attractions into the database if empty."""
    count = db_session.query(Attraction).count()
    if count == 0:
        real_data_path = os.path.join(os.path.dirname(__file__), 'real_data.json')
        if os.path.exists(real_data_path):
            with open(real_data_path, 'r', encoding='utf-8') as f:
                all_attractions_data = json.load(f)
        else:
            # Fallback
            all_attractions_data = ALL_ATTRACTIONS

        print(f"Seeding database with {len(all_attractions_data)} attractions...")
        for attr_data in all_attractions_data:
            attraction = Attraction(**attr_data)
            db_session.add(attraction)
        db_session.commit()
        print("Attractions seed complete!")
    else:
        print(f"Database already has {count} attractions. Skipping attraction seed.")
        
    # Seed a demo user for Render free tier restarts
    user_count = db_session.query(User).count()
    if user_count == 0:
        print("Seeding demo user...")
        demo_user = User(
            email="demo@example.com",
            username="demouser",
            full_name="Demo User",
            hashed_password=hash_password("password123")
        )
        db_session.add(demo_user)
        db_session.commit()
        db_session.refresh(demo_user)
        
        # Add a default profile for them
        demo_profile = TravelerProfile(
            user_id=demo_user.id,
            archetype="High-Energy Social Explorer",
            archetype_explanation="You love fast-paced travel, bustling crowds, and exciting nightlife.",
            travel_pace=5, budget_per_day=4, crowd_tolerance=5,
            food_adventurousness=4, cultural_curiosity=2, adventure_appetite=4,
            climate_tolerance=3, photography_interest=4, nightlife_interest=5,
            relaxation_preference=1, luxury_preference=3, social_preference=5,
            planning_spontaneity=4, walking_tolerance=4, local_experience=2
        )
        db_session.add(demo_profile)
        db_session.commit()
        print("Demo user created successfully! Email: demo@example.com / Password: password123")
