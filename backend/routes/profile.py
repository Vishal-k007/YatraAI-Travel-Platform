"""
Traveler Profile API Routes.
Handles submission of the personality quiz and returning the generated ML archetype.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User, TravelerProfile
from schemas import QuizSubmission, ProfileResponse, ClusterVisualization
from auth import get_current_user
from ml.profiler import profiler

router = APIRouter()

@router.post("/quiz", response_model=ProfileResponse)
def submit_quiz(
    quiz: QuizSubmission, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit personality quiz (15 questions).
    Passes data to ML K-Means model to compute traveler archetype.
    Saves/updates profile in DB.
    """
    quiz_dict = quiz.dict()
    
    # 1. Run ML Prediction
    try:
        prediction = profiler.predict_profile(quiz_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML Profiling Error: {str(e)}")
        
    # 2. Check if profile already exists
    profile = db.query(TravelerProfile).filter(TravelerProfile.user_id == current_user.id).first()
    
    if profile:
        # Update existing
        for key, value in quiz_dict.items():
            setattr(profile, key, value)
        profile.archetype = prediction["archetype"]
        profile.cluster_id = prediction["cluster_id"]
        profile.archetype_explanation = prediction["archetype_explanation"]
        profile.archetype_scores = {"traits": prediction["traits"], "pca": prediction["pca_coordinates"]}
    else:
        # Create new
        profile = TravelerProfile(
            user_id=current_user.id,
            **quiz_dict,
            archetype=prediction["archetype"],
            cluster_id=prediction["cluster_id"],
            archetype_explanation=prediction["archetype_explanation"],
            archetype_scores={"traits": prediction["traits"], "pca": prediction["pca_coordinates"]}
        )
        db.add(profile)
        
    db.commit()
    db.refresh(profile)
    return profile

@router.get("/me", response_model=ProfileResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch the authenticated user's travel profile."""
    profile = db.query(TravelerProfile).filter(TravelerProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Please take the quiz first.")
    return profile

@router.get("/visualization", response_model=ClusterVisualization)
def get_cluster_visualization(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns data needed by frontend Recharts/D3 to visualize
    where the user sits in the ML cluster space compared to others.
    """
    profile = db.query(TravelerProfile).filter(TravelerProfile.user_id == current_user.id).first()
    
    clusters_info = [
        {"id": k, "name": v["name"], "traits": v["traits"]}
        for k, v in profiler.archetypes.items()
    ]
    
    user_pos = profile.archetype_scores.get("pca") if profile and profile.archetype_scores else None
    
    # Generate some dummy PCA scatter points for the background visualization
    # In a real app, this would be actual anonymized user data from the DB
    import numpy as np
    np.random.seed(42)
    pca_points = []
    for c_id in profiler.archetypes.keys():
        center_x, center_y = np.random.uniform(-3, 3, 2) # Mock centers
        for _ in range(20): # 20 points per cluster
            x = center_x + np.random.normal(0, 0.5)
            y = center_y + np.random.normal(0, 0.5)
            pca_points.append({"x": x, "y": y, "cluster_id": c_id})
            
    return {
        "clusters": clusters_info,
        "user_position": user_pos,
        "pca_data": pca_points
    }
