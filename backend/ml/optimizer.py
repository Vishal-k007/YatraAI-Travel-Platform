"""
Route and Energy Optimizer Engine.
Takes a list of matched attractions and constructs a geographic, energy-balanced,
time-slotted itinerary spanning multiple days.
"""
import math
from typing import List, Dict, Any

class ItineraryOptimizer:
    def __init__(self):
        # Average speeds in km/h depending on the city terrain
        self.speeds = {
            "Goa": 30.0,
            "Jaipur": 25.0,
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
        """Estimates travel time in minutes."""
        speed = self.speeds.get(city, 25.0)
        hours = dist_km / speed
        return round(hours * 60)

    def _get_time_label(self, hour: float) -> str:
        h = int(hour)
        m = int((hour - h) * 60)
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
        Constructs a complete itinerary.
        Constraints:
        - Max energy per day (based on user profile)
        - Max time per day (e.g., 9 AM to 8 PM)
        - Geographical grouping (clustering daily spots)
        """
        # 1. Filter and sort attractions by score
        # Only take attractions with score > 0.4 to ensure quality
        valid_attractions = [a for a in scored_attractions if a['score'] > 0.4]
        valid_attractions.sort(key=lambda x: x['score'], reverse=True)
        
        # User limits
        # Max energy per day: higher pace/adventure = more energy capacity
        base_energy = 10.0
        pace_multiplier = user_profile.get('travel_pace', 3.0) / 3.0
        max_daily_energy = base_energy * pace_multiplier
        
        # 2. Cluster attractions geographically by day (K-Means simplified)
        # For simplicity, we just use a greedy approach: start with the highest scored,
        # then find nearest neighbors until day is full.
        
        available = valid_attractions.copy()
        days_data = []
        
        current_budget = 0.0
        
        for day in range(1, num_days + 1):
            day_plan = {
                "day_number": day,
                "date_label": f"Day {day}",
                "theme": "",
                "slots": [],
                "total_energy": 0.0,
                "total_cost": 0.0,
                "total_travel_time_mins": 0.0
            }
            
            if not available:
                break
                
            # Pick seed for the day: highest scoring available
            current_loc = available.pop(0)
            
            # Start day at 9:00 AM
            current_time = 9.0 
            day_energy = current_loc['attraction'].get('physical_intensity', 2.0)
            
            # Add Morning Attraction
            start_label = self._get_time_label(current_time)
            duration = current_loc['attraction'].get('avg_visit_duration_hours', 2.0)
            current_time += duration
            end_label = self._get_time_label(current_time)
            
            cost = current_loc['attraction'].get('cost_estimate_inr', 0)
            
            slot = {
                "slot_type": "attraction",
                "time_label": f"{start_label} - {end_label}",
                "period": "morning",
                "attraction_id": current_loc['attraction']['id'],
                "attraction_name": current_loc['attraction']['name'],
                "description": current_loc['attraction']['description'],
                "duration_hours": duration,
                "estimated_cost": cost,
                "energy_level": current_loc['attraction']['physical_intensity'],
                "travel_time_mins": 0, # First of the day
                "recommendation_reason": current_loc['reason'],
                "order_index": 1,
                "latitude": current_loc['attraction']['latitude'],
                "longitude": current_loc['attraction']['longitude'],
                "category": current_loc['attraction']['category']
            }
            day_plan['slots'].append(slot)
            day_plan['total_energy'] += slot['energy_level']
            day_plan['total_cost'] += cost
            current_budget += cost
            
            # Add Lunch Break
            lunch_duration = 1.5
            start_label = self._get_time_label(current_time)
            current_time += lunch_duration
            end_label = self._get_time_label(current_time)
            lunch_cost = 500 if user_profile.get('budget_per_day', 3) < 4 else 1500
            
            day_plan['slots'].append({
                "slot_type": "lunch",
                "time_label": f"{start_label} - {end_label}",
                "period": "afternoon",
                "description": "Local culinary experience nearby.",
                "duration_hours": lunch_duration,
                "estimated_cost": lunch_cost,
                "energy_level": 0.5,
                "travel_time_mins": 10,
                "order_index": 2
            })
            day_plan['total_cost'] += lunch_cost
            current_budget += lunch_cost
            
            # Fill remaining day (until ~7 PM = 19.0)
            slot_index = 3
            last_lat = current_loc['attraction']['latitude']
            last_lon = current_loc['attraction']['longitude']
            
            while current_time < 18.0 and available and day_plan['total_energy'] < max_daily_energy:
                # Find best next attraction: trade-off between score and distance
                best_next_idx = -1
                best_heuristic = -float('inf')
                
                for i, cand in enumerate(available):
                    cand_cost = cand['attraction'].get('cost_estimate_inr', 0)
                    # Budget constraint check
                    if budget_limit and (current_budget + cand_cost > budget_limit) and cand_cost > 0:
                        continue
                        
                    dist = self.haversine_distance(
                        last_lat, last_lon, 
                        cand['attraction']['latitude'], cand['attraction']['longitude']
                    )
                    
                    # Heuristic: Score highly, penalize distance heavily
                    # If distance is > 20km, heavily penalize to keep it clustered
                    dist_penalty = (dist / 5.0) if dist > 0 else 0
                    heuristic = cand['score'] - dist_penalty
                    
                    if heuristic > best_heuristic:
                        best_heuristic = heuristic
                        best_next_idx = i
                
                if best_next_idx == -1:
                    break # No suitable candidates left
                    
                next_loc = available.pop(best_next_idx)
                
                # Calculate travel
                dist_km = self.haversine_distance(
                    last_lat, last_lon, 
                    next_loc['attraction']['latitude'], next_loc['attraction']['longitude']
                )
                travel_mins = self._estimate_travel_time(dist_km, city)
                
                current_time += (travel_mins / 60.0)
                
                # Add Attraction
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
                current_budget += cost
                
                last_lat = next_loc['attraction']['latitude']
                last_lon = next_loc['attraction']['longitude']
                slot_index += 1
                
            # Define Theme based on categories
            cats = [s.get('category') for s in day_plan['slots'] if s.get('category')]
            if cats:
                top_cat = max(set(cats), key=cats.count)
                day_plan['theme'] = f"{top_cat} Exploration Day"
            else:
                day_plan['theme'] = "Discovery Day"
                
            days_data.append(day_plan)
            
        # Compile full itinerary metadata
        total_cost = sum(d['total_cost'] for d in days_data)
        total_energy = sum(d['total_energy'] for d in days_data)
        avg_daily_energy = total_energy / len(days_data) if days_data else 0
        total_attractions = sum(1 for d in days_data for s in d['slots'] if s['slot_type'] == 'attraction')
        
        # Collect overall explanations
        reasons = {}
        for d in days_data:
            for s in d['slots']:
                if s['slot_type'] == 'attraction':
                    reasons[s['attraction_name']] = s.get('recommendation_reason', '')
                    
        return {
            "city": city,
            "num_days": num_days,
            "total_estimated_cost": total_cost,
            "total_attractions": total_attractions,
            "avg_daily_energy": avg_daily_energy,
            "days": days_data,
            "recommendations_explanation": reasons,
            "warnings": ["Pace may be high today." if avg_daily_energy > 8.0 else "Relaxed pace."]
        }

route_optimizer = ItineraryOptimizer()
