"""
Route and Energy Optimizer Engine.
Takes a list of matched attractions and constructs a geographic, energy-balanced,
time-slotted itinerary spanning multiple days. Features realistic budgeting, clustering, and AI explanations.
"""
import math
from typing import List, Dict, Any

from ml.restaurant_recommender import restaurant_recommender


MIN_ATTRACTIONS_PER_DAY = 2


class ItineraryOptimizer:
    def __init__(self):
        # Average speeds in km/h depending on the city terrain
        self.speeds = {
            "Goa": 30.0,
            "Jaipur": 20.0, # Slower traffic
            "Manali": 15.0 # Mountainous, slow roads
        }
        
    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the great circle distance between two points on the earth (in km)."""
        R = 6371.0  # Earth radius in km
        lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
        lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
        
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def _estimate_travel_time(self, dist_km: float, city: str) -> float:
        """Estimates realistic travel time in minutes including buffer."""
        speed = self.speeds.get(city, 20.0)
        hours = dist_km / speed
        raw_mins = hours * 60
        # Add 10 mins buffer for parking/walking to entrance
        return round(raw_mins + 10)

    def _get_time_label(self, hour: float) -> str:
        h = int(hour)
        m = int((hour - h) * 60)
        # Normalize past midnight if any
        if h >= 24: h -= 24
        period = "AM" if h < 12 else "PM"
        display_h = h if h <= 12 else h - 12
        if display_h == 0: display_h = 12
        return f"{display_h:02d}:{m:02d} {period}"

    def _attraction_count(self, day_plan: dict) -> int:
        return sum(1 for s in day_plan["slots"] if s["slot_type"] == "attraction")

    def _day_attraction_ids(self, day_plan: dict) -> set:
        return {s["attraction_id"] for s in day_plan["slots"] if s.get("attraction_id")}

    def _build_attraction_slot(
        self,
        loc: Dict[str, Any],
        start_hour: float,
        order_index: int,
        period: str,
        travel_mins: float,
    ) -> tuple[dict, float]:
        """Build attraction slot dict and return (slot, end_hour)."""
        attr = loc["attraction"]
        duration = attr.get("avg_visit_duration_hours", 2.0)
        end_hour = start_hour + duration
        cost = attr.get("cost_estimate_inr", 0) or 0
        start_label = self._get_time_label(start_hour)
        end_label = self._get_time_label(end_hour)

        slot = {
            "slot_type": "attraction",
            "time_label": f"{start_label} - {end_label}",
            "period": period,
            "attraction_id": attr["id"],
            "attraction_name": attr["name"],
            "description": attr["description"],
            "image_url": attr.get("image_url", ""),
            "image_urls": attr.get("image_urls") or [],
            "duration_hours": duration,
            "estimated_cost": cost,
            "cost_estimate_inr": cost,
            "cost_breakdown": attr.get("cost_breakdown") or {},
            "best_visiting_time": attr.get("best_visiting_time"),
            "energy_level": attr.get("physical_intensity", 2.0),
            "travel_time_mins": travel_mins,
            "recommendation_reason": loc["reason"],
            "order_index": order_index,
            "latitude": attr["latitude"],
            "longitude": attr["longitude"],
            "category": attr["category"],
        }
        return slot, end_hour

    def _refresh_available_for_day(
        self,
        available: List[Dict[str, Any]],
        valid_attractions: List[Dict[str, Any]],
        day_plan: dict,
    ) -> List[Dict[str, Any]]:
        used_ids = self._day_attraction_ids(day_plan)
        refreshed = [a for a in valid_attractions if a["attraction"]["id"] not in used_ids]
        return refreshed if refreshed else valid_attractions.copy()

    def generate_itinerary(self, 
                           city: str, 
                           num_days: int, 
                           user_profile: dict, 
                           scored_attractions: List[Dict[str, Any]],
                           budget_limit: float = None,
                           stay_budget: float = 1000.0,
                           food_budget: float = 1000.0) -> dict:
        """
        Constructs a complete itinerary with dynamic pacing, realistic budget, and clustering.
        """
        # Filter and sort by score
        valid_attractions = [a for a in scored_attractions if a['score'] > 0.35]
        
        # Ensure we have enough attractions for the requested days (at least 3 per day)
        if len(valid_attractions) < num_days * 3:
            valid_attractions = sorted(scored_attractions, key=lambda x: x['score'], reverse=True)[:max(num_days*4, len(scored_attractions))]
        else:
            valid_attractions.sort(key=lambda x: x['score'], reverse=True)
            
        if not valid_attractions:
             valid_attractions = scored_attractions.copy()
        
        # Base limits scaled by day count and profile
        base_energy = 12.0
        # Longer trips mean more relaxed pacing
        day_pace_factor = 1.0 if num_days <= 2 else (0.85 if num_days <= 4 else 0.7)
        user_pace = user_profile.get('travel_pace', 3.0) / 3.0
        max_daily_energy = base_energy * user_pace * day_pace_factor
        
        # Ensure budget fits user style (1-5)
        user_budget_pref = user_profile.get('budget_per_day', 3)
        daily_food_budget = food_budget if food_budget is not None else 1000.0
        local_transport_budget = 500 if user_budget_pref < 3 else (1200 if user_budget_pref == 3 else 3000)
        
        if budget_limit:
            daily_budget_target = budget_limit / num_days
            base_daily = daily_food_budget + local_transport_budget
            # Reserve at least 30% of daily budget for attractions
            if base_daily > daily_budget_target * 0.7:
                scale_factor = (daily_budget_target * 0.7) / base_daily if base_daily > 0 else 0
                daily_food_budget = int(daily_food_budget * scale_factor)
                local_transport_budget = int(local_transport_budget * scale_factor)
        
        available = valid_attractions.copy()
        days_data = []
        used_restaurants: set[str] = set()
        
        total_estimated_cost = 0.0
        
        for day in range(1, num_days + 1):
            # Dynamic start time based on relaxation preference
            relax_pref = user_profile.get('relaxation_preference', 3.0)
            current_time = 8.5 + (0.5 * (relax_pref - 1)) # Starts between 8:30 and 10:30
            
            day_plan = {
                "day_number": day,
                "date_label": f"Day {day}",
                "theme": "",
                "slots": [],
                "total_energy": 0.0,
                "total_cost": daily_food_budget + local_transport_budget,
                "total_travel_time_mins": 0.0
            }
            total_estimated_cost += day_plan['total_cost']
            
            if not available:
                available = valid_attractions.copy()
                if not available:
                    break
                
            # Pick seed for the day: highest scoring available, preferably matching time of day
            best_seed_idx = -1
            for idx, a in enumerate(available[:5]):
                cost_cand = a['attraction'].get('cost_estimate_inr', 0)
                if budget_limit and total_estimated_cost + cost_cand > budget_limit:
                    continue
                if a['attraction']['best_visiting_time'] in ['Morning', 'Any']:
                    best_seed_idx = idx
                    break
                    
            if best_seed_idx == -1:
                for idx, a in enumerate(available):
                    cost_cand = a['attraction'].get('cost_estimate_inr', 0)
                    if not budget_limit or total_estimated_cost + cost_cand <= budget_limit:
                        best_seed_idx = idx
                        break
            
            if best_seed_idx == -1:
                # Even if no affordable attractions left, we should continue to provide the day frame
                current_loc = valid_attractions[0] # Fallback, might exceed budget slightly, or we could just add empty slots. Let's just pick cheapest.
                cheapest_idx = min(range(len(available)), key=lambda i: available[i]['attraction'].get('cost_estimate_inr', 0))
                current_loc = available.pop(cheapest_idx)
            else:
                current_loc = available.pop(best_seed_idx)
            
            # Breakfast — famous restaurant near today's first stop
            bf_lat = current_loc['attraction']['latitude']
            bf_lon = current_loc['attraction']['longitude']
            breakfast = restaurant_recommender.recommend(
                city, "breakfast", bf_lat, bf_lon, used_restaurants, daily_food_budget,
            )
            if breakfast:
                used_restaurants.add(breakfast["restaurant_name"])
                breakfast_cost = breakfast["estimated_cost"]
            else:
                breakfast_cost = int(daily_food_budget * 0.2)
                breakfast = {
                    "attraction_name": "Local Breakfast Spot",
                    "description": "Start your day with a hearty local breakfast.",
                    "estimated_cost": breakfast_cost,
                }
            day_plan['slots'].append({
                "slot_type": "breakfast",
                "time_label": f"{self._get_time_label(current_time - 1.0)} - {self._get_time_label(current_time - 0.25)}",
                "period": "morning",
                "description": breakfast["description"],
                "attraction_name": breakfast.get("attraction_name"),
                "restaurant_name": breakfast.get("restaurant_name"),
                "restaurant_area": breakfast.get("restaurant_area"),
                "cuisine_type": breakfast.get("cuisine_type"),
                "famous_dishes": breakfast.get("famous_dishes"),
                "duration_hours": 0.75,
                "estimated_cost": breakfast_cost,
                "energy_level": 0.2,
                "travel_time_mins": 10,
                "recommendation_reason": breakfast.get("recommendation_reason"),
                "restaurant_vibe": breakfast.get("restaurant_vibe"),
                "restaurant_source": breakfast.get("restaurant_source"),
                "latitude": breakfast.get("latitude"),
                "longitude": breakfast.get("longitude"),
                "order_index": 0,
            })
            day_plan['total_cost'] += breakfast_cost - int(daily_food_budget * 0.2)
            total_estimated_cost += breakfast_cost - int(daily_food_budget * 0.2)
            
            # Add Morning Attraction
            slot, current_time = self._build_attraction_slot(
                current_loc, current_time, 1, "morning", 15
            )
            day_plan['slots'].append(slot)
            day_plan['total_energy'] += slot['energy_level']
            day_plan['total_cost'] += slot['estimated_cost']
            total_estimated_cost += slot['estimated_cost']
            
            last_lat = current_loc['attraction']['latitude']
            last_lon = current_loc['attraction']['longitude']
            
            # Add Lunch Break (around 1 PM)
            current_time += 0.5 # Buffer/travel
            lunch_start = current_time
            if lunch_start < 12.5: lunch_start = 12.5
            elif lunch_start > 14.5: lunch_start = 14.5
            current_time = lunch_start + 1.5
            
            lunch = restaurant_recommender.recommend(
                city, "lunch", last_lat, last_lon, used_restaurants, daily_food_budget,
            )
            if lunch:
                used_restaurants.add(lunch["restaurant_name"])
                lunch_cost = lunch["estimated_cost"]
            else:
                lunch_cost = int(daily_food_budget * 0.4)
                lunch = {
                    "attraction_name": "Local Lunch Spot",
                    "description": "Lunch break at a highly-rated local restaurant nearby.",
                    "estimated_cost": lunch_cost,
                }
            day_plan['slots'].append({
                "slot_type": "lunch",
                "time_label": f"{self._get_time_label(lunch_start)} - {self._get_time_label(current_time)}",
                "period": "afternoon",
                "description": lunch["description"],
                "attraction_name": lunch.get("attraction_name"),
                "restaurant_name": lunch.get("restaurant_name"),
                "restaurant_area": lunch.get("restaurant_area"),
                "cuisine_type": lunch.get("cuisine_type"),
                "famous_dishes": lunch.get("famous_dishes"),
                "duration_hours": 1.5,
                "estimated_cost": lunch_cost,
                "energy_level": 0.5,
                "travel_time_mins": 15,
                "recommendation_reason": lunch.get("recommendation_reason"),
                "restaurant_vibe": lunch.get("restaurant_vibe"),
                "restaurant_source": lunch.get("restaurant_source"),
                "latitude": lunch.get("latitude"),
                "longitude": lunch.get("longitude"),
                "order_index": 2,
            })
            day_plan['total_cost'] += lunch_cost - int(daily_food_budget * 0.4)
            total_estimated_cost += lunch_cost - int(daily_food_budget * 0.4)
            
            # Fill afternoon/evening — at least MIN_ATTRACTIONS_PER_DAY tourist spots per day
            slot_index = 3

            while True:
                attr_count = self._attraction_count(day_plan)
                need_more_spots = attr_count < MIN_ATTRACTIONS_PER_DAY
                if not need_more_spots and (
                    current_time >= 18.0 or day_plan["total_energy"] >= max_daily_energy
                ):
                    break

                if not available:
                    available = self._refresh_available_for_day(
                        available, valid_attractions, day_plan
                    )

                best_next_idx = -1
                best_heuristic = -float("inf")

                for i, cand in enumerate(available):
                    cost_cand = cand["attraction"].get("cost_estimate_inr", 0)
                    if budget_limit and total_estimated_cost + cost_cand > budget_limit:
                        if not need_more_spots:
                            continue

                    dist = self.haversine_distance(
                        last_lat,
                        last_lon,
                        cand["attraction"]["latitude"],
                        cand["attraction"]["longitude"],
                    )
                    dist_penalty = (dist / 2.0) if dist > 0 else 0
                    time_bonus = (
                        0.5
                        if cand["attraction"]["best_visiting_time"]
                        in ["Afternoon", "Evening", "Any"]
                        else 0
                    )
                    heuristic = cand["score"] + time_bonus - dist_penalty

                    if heuristic > best_heuristic:
                        best_heuristic = heuristic
                        best_next_idx = i

                if best_next_idx == -1:
                    if need_more_spots:
                        available = self._refresh_available_for_day(
                            available, valid_attractions, day_plan
                        )
                        if not available:
                            break
                        best_next_idx = max(
                            range(len(available)),
                            key=lambda i: available[i]["score"],
                        )
                    else:
                        break

                next_loc = available.pop(best_next_idx)

                dist_km = self.haversine_distance(
                    last_lat,
                    last_lon,
                    next_loc["attraction"]["latitude"],
                    next_loc["attraction"]["longitude"],
                )
                travel_mins = self._estimate_travel_time(dist_km, city)
                duration = next_loc["attraction"].get("avg_visit_duration_hours", 2.0)
                if need_more_spots and attr_count == 1:
                    duration = min(duration, 2.0)

                max_end_hour = 20.5 if need_more_spots else 20.0
                if current_time + (travel_mins / 60.0) + duration > max_end_hour:
                    available.append(next_loc)
                    if need_more_spots and attr_count >= 1:
                        duration = min(
                            next_loc["attraction"].get("avg_visit_duration_hours", 2.0),
                            max(1.0, max_end_hour - current_time - travel_mins / 60.0),
                        )
                        if duration < 0.75:
                            break
                    else:
                        break

                current_time += travel_mins / 60.0
                period = "afternoon" if current_time < 17.0 else "evening"
                slot, current_time = self._build_attraction_slot(
                    next_loc, current_time, slot_index, period, travel_mins
                )
                if need_more_spots and attr_count == 1:
                    slot["duration_hours"] = duration
                    end_hour = current_time - duration + duration
                    slot["time_label"] = (
                        f"{self._get_time_label(current_time - duration)} - "
                        f"{self._get_time_label(current_time)}"
                    )

                day_plan["slots"].append(slot)
                day_plan["total_energy"] += slot["energy_level"]
                day_plan["total_cost"] += slot["estimated_cost"]
                day_plan["total_travel_time_mins"] += travel_mins
                total_estimated_cost += slot["estimated_cost"]

                last_lat = next_loc["attraction"]["latitude"]
                last_lon = next_loc["attraction"]["longitude"]
                slot_index += 1
                
            # Dinner
            current_time += 0.5
            dinner_start = current_time if current_time > 19.0 else 19.0
            
            dinner = restaurant_recommender.recommend(
                city, "dinner", last_lat, last_lon, used_restaurants, daily_food_budget,
            )
            if dinner:
                used_restaurants.add(dinner["restaurant_name"])
                dinner_cost = dinner["estimated_cost"]
            else:
                dinner_cost = int(daily_food_budget * 0.4)
                dinner = {
                    "attraction_name": "Local Dinner Spot",
                    "description": "Relax and enjoy a delicious dinner to end your day.",
                    "estimated_cost": dinner_cost,
                }
            day_plan['slots'].append({
                "slot_type": "dinner",
                "time_label": f"{self._get_time_label(dinner_start)} - {self._get_time_label(dinner_start + 1.5)}",
                "period": "night",
                "description": dinner["description"],
                "attraction_name": dinner.get("attraction_name"),
                "restaurant_name": dinner.get("restaurant_name"),
                "restaurant_area": dinner.get("restaurant_area"),
                "cuisine_type": dinner.get("cuisine_type"),
                "famous_dishes": dinner.get("famous_dishes"),
                "duration_hours": 1.5,
                "estimated_cost": dinner_cost,
                "energy_level": 0.5,
                "travel_time_mins": 20,
                "recommendation_reason": dinner.get("recommendation_reason"),
                "restaurant_vibe": dinner.get("restaurant_vibe"),
                "restaurant_source": dinner.get("restaurant_source"),
                "latitude": dinner.get("latitude"),
                "longitude": dinner.get("longitude"),
                "order_index": slot_index,
            })
            day_plan['total_cost'] += dinner_cost - int(daily_food_budget * 0.4)
            total_estimated_cost += dinner_cost - int(daily_food_budget * 0.4)
            
            # Stay / Accommodation
            stay_options = {
                "Goa": [
                    {"name": "Zostel Goa", "type": "Hostel", "source": "Booking.com", "cost": 600, "desc": "Lively hostel near the beach with great vibes."},
                    {"name": "Seaside Budget Homestay", "type": "Homestay", "source": "Airbnb", "cost": 1200, "desc": "Cozy homestay with local Goan breakfast included."},
                    {"name": "Panjim Heritage Inn", "type": "Hotel", "source": "Google Hotels", "cost": 1800, "desc": "Classic Portuguese style inn in the heart of Panjim."},
                ],
                "Jaipur": [
                    {"name": "Moustache Hostel Jaipur", "type": "Hostel", "source": "Booking.com", "cost": 500, "desc": "Rooftop views of Nahargarh Fort, great for solo travelers."},
                    {"name": "Pink City Heritage Guest House", "type": "Guesthouse", "source": "Airbnb", "cost": 1100, "desc": "Authentic Rajasthani decor and warm hospitality."},
                    {"name": "Boutique Palace Stay", "type": "Hotel", "source": "Google Hotels", "cost": 1900, "desc": "Experience royal living on a budget with a courtyard pool."},
                ],
                "Manali": [
                    {"name": "Alt Life - Manali", "type": "Hostel", "source": "Booking.com", "cost": 700, "desc": "Mountain views and cafe in Old Manali."},
                    {"name": "Apple Orchard Homestay", "type": "Homestay", "source": "Airbnb", "cost": 1400, "desc": "Wake up to snow-capped peaks and fresh apples."},
                    {"name": "River View Retreat", "type": "Resort", "source": "Google Hotels", "cost": 2000, "desc": "Comfortable stay right next to the Beas river."},
                ]
            }
            city_stays = stay_options.get(city, stay_options["Goa"])
            budget_to_use = stay_budget if stay_budget is not None else 1000.0
            valid_stays = [s for s in city_stays if s["cost"] <= budget_to_use]
            stay = max(valid_stays, key=lambda x: x["cost"]) if valid_stays else min(city_stays, key=lambda x: x["cost"])
            
            day_plan['slots'].append({
                "slot_type": "stay",
                "time_label": "Overnight",
                "period": "night",
                "description": f"{stay['desc']} (Data sourced from {stay['source']})",
                "attraction_name": stay["name"],
                "stay_name": stay["name"],
                "stay_type": stay["type"],
                "stay_source": stay["source"],
                "estimated_cost": stay["cost"],
                "duration_hours": 0.0,
                "energy_level": 0.0,
                "travel_time_mins": 0.0,
                "order_index": slot_index + 1,
            })
            day_plan['total_cost'] += stay["cost"]
            total_estimated_cost += stay["cost"]
            
            
            # Theme based on categories
            cats = [s.get('category') for s in day_plan['slots'] if s.get('category') and s['slot_type'] == 'attraction']
            if cats:
                top_cat = max(set(cats), key=cats.count)
                day_plan['theme'] = f"{top_cat} & Local Vibes"
            else:
                day_plan['theme'] = "Leisure & Culinary Day"
                
            days_data.append(day_plan)
            
        total_energy = sum(d['total_energy'] for d in days_data)
        avg_daily_energy = total_energy / len(days_data) if days_data else 0
        total_attractions = sum(1 for d in days_data for s in d['slots'] if s['slot_type'] == 'attraction')
        
        reasons = {}
        for d in days_data:
            for s in d['slots']:
                if s['slot_type'] == 'attraction':
                    # Add AI explanation text based on category
                    match_quality = s.get('recommendation_reason', '')
                    intensity_match = "Fits your requested pace perfectly." if s['energy_level'] <= user_pace * 5 else "A bit challenging but rewarding."
                    reasons[s['attraction_name']] = f"{match_quality} {intensity_match} Highly rated for {s.get('category', 'its unique experience')}."
                    
        return {
            "city": city,
            "num_days": num_days,
            "total_estimated_cost": total_estimated_cost,
            "total_attractions": total_attractions,
            "avg_daily_energy": avg_daily_energy,
            "days": days_data,
            "recommendations_explanation": reasons,
            "warnings": ["Pace may be high today. Remember to stay hydrated!" if avg_daily_energy > 8.0 else "Relaxed pace itinerary, enjoy your trip!"]
        }

route_optimizer = ItineraryOptimizer()
