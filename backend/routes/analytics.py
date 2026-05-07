"""
Analytics API Routes.
Provides aggregate data for the dashboard.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import User, Itinerary, TravelerProfile, Attraction, Favorite
from schemas import AnalyticsResponse
from auth import get_current_user

router = APIRouter()

@router.get("/", response_model=AnalyticsResponse)
def get_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Require auth, could restrict to admin
):
    """Get platform-wide analytics for the dashboard."""
    
    total_users = db.query(User).count()
    total_itineraries = db.query(Itinerary).count()
    
    # Popular cities
    city_counts = db.query(Itinerary.city, func.count(Itinerary.id)).group_by(Itinerary.city).all()
    popular_cities = {city: count for city, count in city_counts}
    
    # Archetype distribution
    arch_counts = db.query(TravelerProfile.archetype, func.count(TravelerProfile.id)).group_by(TravelerProfile.archetype).all()
    archetype_distribution = {arch if arch else "Pending": count for arch, count in arch_counts}
    
    # Avg trip duration
    avg_duration = db.query(func.avg(Itinerary.num_days)).scalar() or 0.0
    
    # Top favorites
    top_favs = db.query(Favorite.attraction_id, func.count(Favorite.id).label('count')).group_by(Favorite.attraction_id).order_by(func.count(Favorite.id).desc()).limit(5).all()
    
    top_attractions = []
    for fav in top_favs:
        attr = db.query(Attraction).filter(Attraction.id == fav.attraction_id).first()
        if attr:
            top_attractions.append({
                "id": attr.id,
                "name": attr.name,
                "city": attr.city,
                "favorite_count": fav.count
            })
            
    return {
        "total_users": total_users,
        "total_itineraries": total_itineraries,
        "popular_cities": popular_cities,
        "archetype_distribution": archetype_distribution,
        "avg_trip_duration": float(avg_duration),
        "top_attractions": top_attractions
    }
