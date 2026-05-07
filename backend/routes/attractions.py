"""
Attractions API Routes.
Provides endpoints to search, filter, and score attractions based on ML compatibility.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import User, Attraction, Favorite, TravelerProfile
from schemas import AttractionResponse
from auth import get_current_user
from ml.match_scorer import match_scorer

router = APIRouter()

@router.get("/", response_model=List[AttractionResponse])
def get_attractions(
    city: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch attractions, optionally filtered by city and category.
    If user has a profile, computes ML match score for each attraction.
    """
    query = db.query(Attraction)
    
    if city:
        query = query.filter(Attraction.city == city)
    if category:
        query = query.filter(Attraction.category == category)
        
    attractions = query.all()
    
    # Fetch user favorites
    favorites = {f.attraction_id for f in db.query(Favorite).filter(Favorite.user_id == current_user.id).all()}
    
    # Fetch user profile for ML scoring
    profile = db.query(TravelerProfile).filter(TravelerProfile.user_id == current_user.id).first()
    
    results = []
    for attr in attractions:
        # Convert DB object to dict for response
        attr_dict = {c.name: getattr(attr, c.name) for c in attr.__table__.columns}
        attr_dict["is_favorite"] = attr.id in favorites
        
        # Calculate ML Score
        if profile:
            profile_dict = {c.name: getattr(profile, c.name) for c in profile.__table__.columns}
            match_res = match_scorer.calculate_match_score(profile_dict, attr_dict)
            attr_dict["match_score"] = round(match_res["score"] * 100) # Convert to percentage
            attr_dict["match_reason"] = match_res["reason"]
        else:
            attr_dict["match_score"] = None
            attr_dict["match_reason"] = None
            
        results.append(attr_dict)
        
    # Sort by match score if profile exists
    if profile:
        results.sort(key=lambda x: x["match_score"] or 0, reverse=True)
        
    return results

@router.post("/{attraction_id}/favorite")
def toggle_favorite(
    attraction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Toggle favorite status for an attraction."""
    fav = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.attraction_id == attraction_id
    ).first()
    
    if fav:
        db.delete(fav)
        db.commit()
        return {"status": "removed"}
    else:
        new_fav = Favorite(user_id=current_user.id, attraction_id=attraction_id)
        db.add(new_fav)
        db.commit()
        return {"status": "added"}
