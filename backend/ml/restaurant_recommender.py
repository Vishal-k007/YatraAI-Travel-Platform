"""
Recommends famous nearby restaurants for breakfast, lunch, and dinner slots.
"""
import math
from typing import Any

from data.restaurants import CITY_CENTERS, RESTAURANTS


class RestaurantRecommender:
    def haversine_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        r = 6371.0
        lat1_r, lon1_r = math.radians(lat1), math.radians(lon1)
        lat2_r, lon2_r = math.radians(lat2), math.radians(lon2)
        dlat = lat2_r - lat1_r
        dlon = lon2_r - lon1_r
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
        return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def _budget_tier(self, budget_per_day_inr: float) -> str:
        # budget_per_day_inr is the total food budget per day
        # average 3 meals, so per meal is ~ budget/3
        per_meal = budget_per_day_inr / 3.0
        if per_meal <= 300:
            return "budget"
        if per_meal >= 600:
            return "premium"
        return "mid"

    def _scaled_cost(self, base_cost: int, budget_per_day_inr: float) -> int:
        tier = self._budget_tier(budget_per_day_inr)
        if tier == "budget":
            return min(int(base_cost * 0.8), int(budget_per_day_inr * 0.4))
        if tier == "premium":
            return int(base_cost * 1.2)
        return base_cost

    def recommend(
        self,
        city: str,
        meal_type: str,
        near_lat: float,
        near_lon: float,
        used_restaurants: set[str],
        budget_per_day_inr: float = 1500.0,
    ) -> dict[str, Any] | None:
        candidates = [
            r
            for r in RESTAURANTS
            if r["city"] == city
            and meal_type in r["meal_types"]
            and r["name"] not in used_restaurants
        ]
        if not candidates:
            candidates = [r for r in RESTAURANTS if r["city"] == city and meal_type in r["meal_types"]]
        if not candidates:
            return None

        tier = self._budget_tier(budget_per_day_inr)

        def score(restaurant: dict) -> float:
            dist = self.haversine_km(near_lat, near_lon, restaurant["latitude"], restaurant["longitude"])
            base_cost = restaurant["cost_per_person"].get(meal_type, 600)
            dist_score = max(0, 10 - dist)
            if tier == "budget":
                cost_score = max(0, 5 - (base_cost / 200))
            elif tier == "premium":
                cost_score = min(5, base_cost / 300)
            else:
                cost_score = 2.5
            return dist_score + cost_score

        best = max(candidates, key=score)
        cost = self._scaled_cost(best["cost_per_person"].get(meal_type, 600), budget_per_day_inr)
        dishes = best["famous_dishes"][:4]

        meal_label = meal_type.capitalize()
        return {
            "restaurant_name": best["name"],
            "restaurant_area": best["area"],
            "cuisine_type": best["cuisine"],
            "famous_dishes": dishes,
            "attraction_name": best["name"],
            "description": (
                f"{meal_label} at {best['name']} ({best['area']}) — {best['cuisine']}. "
                f"Must-try: {', '.join(dishes[:3])}."
            ),
            "estimated_cost": cost,
            "latitude": best["latitude"],
            "longitude": best["longitude"],
            "restaurant_vibe": "Local Secret" if tier == "budget" else "Fine Dining" if tier == "premium" else "Famous & Popular",
            "restaurant_source": "Google Local Guides" if tier == "budget" else "Michelin Guide/Zomato" if tier == "premium" else "TripAdvisor",
            "recommendation_reason": (
                f"Highly rated {best['cuisine'].lower()} spot near your route — about "
                f"{self.haversine_km(near_lat, near_lon, best['latitude'], best['longitude']):.1f} km away."
            ),
        }


restaurant_recommender = RestaurantRecommender()
