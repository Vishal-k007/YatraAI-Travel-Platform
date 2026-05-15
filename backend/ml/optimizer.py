"""
Route and Energy Optimizer Engine.
Takes a list of matched attractions and constructs a geographic, energy-balanced,
time-slotted itinerary spanning multiple days. Features realistic budgeting, clustering, and AI explanations.
"""
import math
from typing import List, Dict, Any

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

    def generate_itinerary(self, 
                           city: str, 
                           num_days: int, 
                           user_profile: dict, 
                           scored_attractions: List[Dict[str, Any]],
                           budget_limit: float = None) -> dict:
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
        daily_food_budget = 1000 if user_budget_pref < 3 else (2500 if user_budget_pref == 3 else 5000)
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
            
            # Breakfast
            day_plan['slots'].append({
                "slot_type": "breakfast",
                "time_label": f"{self._get_time_label(current_time - 1.0)} - {self._get_time_label(current_time - 0.25)}",
                "period": "morning",
                "description": "Start your day with a hearty local breakfast.",
                "duration_hours": 0.75,
                "estimated_cost": int(daily_food_budget * 0.2),
                "energy_level": 0.2,
                "travel_time_mins": 0,
                "order_index": 0
            })
            
            # Add Morning Attraction
            start_label = self._get_time_label(current_time)
            duration = current_loc['attraction'].get('avg_visit_duration_hours', 2.0)
            current_time += duration
            end_label = self._get_time_label(current_time)
            cost = current_loc['attraction'].get('cost_estimate_inr', 0)
            energy = current_loc['attraction'].get('physical_intensity', 2.0)
            
            slot = {
                "slot_type": "attraction",
                "time_label": f"{start_label} - {end_label}",
                "period": "morning",
                "attraction_id": current_loc['attraction']['id'],
                "attraction_name": current_loc['attraction']['name'],
                "description": current_loc['attraction']['description'],
                "image_url": current_loc['attraction'].get('image_url', ''),
                "duration_hours": duration,
                "estimated_cost": cost,
                "energy_level": energy,
                "travel_time_mins": 15, # Commute from hotel
                "recommendation_reason": current_loc['reason'],
                "order_index": 1,
                "latitude": current_loc['attraction']['latitude'],
                "longitude": current_loc['attraction']['longitude'],
                "category": current_loc['attraction']['category']
            }
            day_plan['slots'].append(slot)
            day_plan['total_energy'] += energy
            day_plan['total_cost'] += cost
            total_estimated_cost += cost
            
            last_lat = current_loc['attraction']['latitude']
            last_lon = current_loc['attraction']['longitude']
            
            # Add Lunch Break (around 1 PM)
            current_time += 0.5 # Buffer/travel
            lunch_start = current_time
            if lunch_start < 12.5: lunch_start = 12.5
            elif lunch_start > 14.5: lunch_start = 14.5
            current_time = lunch_start + 1.5
            
            day_plan['slots'].append({
                "slot_type": "lunch",
                "time_label": f"{self._get_time_label(lunch_start)} - {self._get_time_label(current_time)}",
                "period": "afternoon",
                "description": "Lunch break. We recommend trying a highly-rated local restaurant nearby.",
                "duration_hours": 1.5,
                "estimated_cost": int(daily_food_budget * 0.4),
                "energy_level": 0.5,
                "travel_time_mins": 15,
                "order_index": 2
            })
            
            # Fill remaining day (until ~6 PM for attractions)
            slot_index = 3
            
            while current_time < 18.0 and day_plan['total_energy'] < max_daily_energy:
                if not available:
                    available = valid_attractions.copy()
                    
                # Find best next attraction: cluster geographically + score
                best_next_idx = -1
                best_heuristic = -float('inf')
                
                for i, cand in enumerate(available):
                    cost_cand = cand['attraction'].get('cost_estimate_inr', 0)
                    if budget_limit and total_estimated_cost + cost_cand > budget_limit:
                        continue
                        
                    dist = self.haversine_distance(
                        last_lat, last_lon, 
                        cand['attraction']['latitude'], cand['attraction']['longitude']
                    )
                    
                    # Heuristic: Score highly, penalize distance heavily to create clusters
                    dist_penalty = (dist / 2.0) if dist > 0 else 0
                    time_bonus = 0.5 if cand['attraction']['best_visiting_time'] in ['Afternoon', 'Evening', 'Any'] else 0
                    heuristic = cand['score'] + time_bonus - dist_penalty
                    
                    if heuristic > best_heuristic:
                        best_heuristic = heuristic
                        best_next_idx = i
                
                if best_next_idx == -1:
                    # Try relaxing budget slightly or stop adding attractions for the day
                    break
                    
                next_loc = available.pop(best_next_idx)
                
                dist_km = self.haversine_distance(
                    last_lat, last_lon, 
                    next_loc['attraction']['latitude'], next_loc['attraction']['longitude']
                )
                travel_mins = self._estimate_travel_time(dist_km, city)
                
                # Check if it fits the day
                if current_time + (travel_mins / 60.0) + next_loc['attraction'].get('avg_visit_duration_hours', 2.0) > 20.0:
                    available.append(next_loc) # Put it back
                    break
                
                current_time += (travel_mins / 60.0)
                
                start_label = self._get_time_label(current_time)
                duration = next_loc['attraction'].get('avg_visit_duration_hours', 2.0)
                current_time += duration
                end_label = self._get_time_label(current_time)
                
                cost = next_loc['attraction'].get('cost_estimate_inr', 0)
                energy = next_loc['attraction'].get('physical_intensity', 2.0)
                period = "afternoon" if current_time < 17.0 else "evening"
                
                slot = {
                    "slot_type": "attraction",
                    "time_label": f"{start_label} - {end_label}",
                    "period": period,
                    "attraction_id": next_loc['attraction']['id'],
                    "attraction_name": next_loc['attraction']['name'],
                    "description": next_loc['attraction']['description'],
                    "image_url": next_loc['attraction'].get('image_url', ''),
                    "duration_hours": duration,
                    "estimated_cost": cost,
                    "energy_level": energy,
                    "travel_time_mins": travel_mins,
                    "recommendation_reason": next_loc['reason'],
                    "order_index": slot_index,
                    "latitude": next_loc['attraction']['latitude'],
                    "longitude": next_loc['attraction']['longitude'],
                    "category": next_loc['attraction']['category']
                }
                day_plan['slots'].append(slot)
                day_plan['total_energy'] += energy
                day_plan['total_cost'] += cost
                day_plan['total_travel_time_mins'] += travel_mins
                total_estimated_cost += cost
                
                last_lat = next_loc['attraction']['latitude']
                last_lon = next_loc['attraction']['longitude']
                slot_index += 1
                
            # Dinner
            current_time += 0.5
            dinner_start = current_time if current_time > 19.0 else 19.0
            
            day_plan['slots'].append({
                "slot_type": "dinner",
                "time_label": f"{self._get_time_label(dinner_start)} - {self._get_time_label(dinner_start + 1.5)}",
                "period": "night",
                "description": "Relax and enjoy a delicious dinner to end your day.",
                "duration_hours": 1.5,
                "estimated_cost": int(daily_food_budget * 0.4),
                "energy_level": 0.5,
                "travel_time_mins": 20,
                "order_index": slot_index
            })
            
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
