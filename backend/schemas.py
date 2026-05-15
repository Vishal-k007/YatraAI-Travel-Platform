"""
Pydantic schemas for request/response validation.
Provides type-safe data contracts between frontend and backend.
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import re


# ============================================================
# Authentication Schemas
# ============================================================

class UserRegister(BaseModel):
    """Schema for user registration request."""
    email: str = Field(..., min_length=5, max_length=255, description="User email")
    username: str = Field(..., min_length=3, max_length=100, description="Unique username")
    password: str = Field(..., min_length=8, max_length=128, description="Password (min 8 chars)")
    full_name: Optional[str] = Field(None, max_length=200, description="Full name")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[^A-Za-z0-9]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserLogin(BaseModel):
    """Schema for user login request."""
    email: str = Field(..., description="User email")
    password: str = Field(..., description="Password")


class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    """Schema for user data in responses."""
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    has_profile: bool = False
    archetype: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================
# Traveler Profile Schemas
# ============================================================

class QuizAnswer(BaseModel):
    """Schema for a single quiz question answer."""
    question_id: str
    value: float = Field(..., ge=1, le=5, description="Answer value from 1 to 5")


class QuizSubmission(BaseModel):
    """Schema for the complete personality quiz submission (15 questions)."""
    travel_pace: float = Field(..., ge=1, le=5)
    budget_per_day: float = Field(..., ge=1, le=5)
    crowd_tolerance: float = Field(..., ge=1, le=5)
    food_adventurousness: float = Field(..., ge=1, le=5)
    cultural_curiosity: float = Field(..., ge=1, le=5)
    adventure_appetite: float = Field(..., ge=1, le=5)
    climate_tolerance: float = Field(..., ge=1, le=5)
    photography_interest: float = Field(..., ge=1, le=5)
    nightlife_interest: float = Field(..., ge=1, le=5)
    relaxation_preference: float = Field(..., ge=1, le=5)
    luxury_preference: float = Field(..., ge=1, le=5)
    social_preference: float = Field(..., ge=1, le=5)
    planning_spontaneity: float = Field(..., ge=1, le=5)
    walking_tolerance: float = Field(..., ge=1, le=5)
    local_experience: float = Field(..., ge=1, le=5)


class ProfileResponse(BaseModel):
    """Schema for traveler profile response with archetype details."""
    id: int
    user_id: int
    archetype: Optional[str] = None
    cluster_id: Optional[int] = None
    archetype_explanation: Optional[str] = None
    archetype_scores: Optional[Dict[str, Any]] = None
    travel_pace: float
    budget_per_day: float
    crowd_tolerance: float
    food_adventurousness: float
    cultural_curiosity: float
    adventure_appetite: float
    climate_tolerance: float
    photography_interest: float
    nightlife_interest: float
    relaxation_preference: float
    luxury_preference: float
    social_preference: float
    planning_spontaneity: float
    walking_tolerance: float
    local_experience: float
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================
# Attraction Schemas
# ============================================================

class AttractionResponse(BaseModel):
    """Schema for attraction data in responses."""
    id: int
    name: str
    city: str
    category: str
    description: str
    image_url: Optional[str] = None
    latitude: float
    longitude: float
    avg_visit_duration_hours: float
    cost_estimate_inr: float
    best_visiting_time: str
    crowd_density: float
    physical_intensity: float
    photography_score: float
    food_availability: float
    family_friendliness: float
    adventure_level: float
    cultural_depth: float
    nightlife_score: float
    weather_sensitivity: float
    is_indoor: bool
    recommended_archetypes: Optional[List[str]] = None
    is_favorite: Optional[bool] = False
    match_score: Optional[float] = None
    match_reason: Optional[str] = None

    class Config:
        from_attributes = True


class AttractionFilter(BaseModel):
    """Schema for filtering attractions."""
    city: Optional[str] = None
    category: Optional[str] = None
    min_budget: Optional[float] = None
    max_budget: Optional[float] = None
    indoor_only: Optional[bool] = None


# ============================================================
# Itinerary Schemas
# ============================================================

class ItineraryRequest(BaseModel):
    """Schema for itinerary generation request."""
    city: str = Field(..., description="Target city: Goa, Jaipur, or Manali")
    num_days: int = Field(..., ge=1, le=7, description="Number of days (1-7)")
    budget_total: Optional[float] = Field(None, description="Total budget in INR")
    preferences: Optional[Dict[str, Any]] = Field(None, description="Additional preferences")


class SlotResponse(BaseModel):
    """Schema for a single itinerary time slot."""
    slot_type: str
    time_label: str
    period: str
    attraction_id: Optional[int] = None
    attraction_name: Optional[str] = None
    description: Optional[str] = None
    duration_hours: Optional[float] = None
    estimated_cost: Optional[float] = None
    energy_level: Optional[float] = None
    travel_time_mins: Optional[float] = None
    recommendation_reason: Optional[str] = None
    order_index: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None
    category: Optional[str] = None


class DayResponse(BaseModel):
    """Schema for a single day in the itinerary."""
    day_number: int
    date_label: Optional[str] = None
    total_energy: Optional[float] = None
    total_cost: Optional[float] = None
    total_travel_time_mins: Optional[float] = None
    theme: Optional[str] = None
    slots: List[SlotResponse] = []


class ItineraryResponse(BaseModel):
    """Schema for complete itinerary response."""
    id: int
    city: str
    num_days: int
    title: Optional[str] = None
    total_estimated_cost: Optional[float] = None
    total_attractions: Optional[int] = None
    avg_daily_energy: Optional[float] = None
    match_score: Optional[float] = None
    days: List[DayResponse] = []
    recommendations_explanation: Optional[Dict[str, Any]] = None
    warnings: Optional[List[str]] = None
    budget_breakdown: Optional[Dict[str, float]] = None
    energy_breakdown: Optional[List[Dict[str, Any]]] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ItineraryListItem(BaseModel):
    """Schema for itinerary in list views."""
    id: int
    city: str
    num_days: int
    title: Optional[str] = None
    total_estimated_cost: Optional[float] = None
    total_attractions: Optional[int] = None
    match_score: Optional[float] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================
# Analytics Schemas
# ============================================================

class ClusterVisualization(BaseModel):
    """Schema for cluster visualization data."""
    clusters: List[Dict[str, Any]]
    user_position: Optional[Dict[str, float]] = None
    pca_data: Optional[List[Dict[str, Any]]] = None
    cluster_centers: Optional[List[Dict[str, float]]] = None


class AnalyticsResponse(BaseModel):
    """Schema for analytics dashboard data."""
    total_users: int
    total_itineraries: int
    popular_cities: Dict[str, int]
    archetype_distribution: Dict[str, int]
    avg_trip_duration: float
    top_attractions: List[Dict[str, Any]]


# Forward reference resolution
TokenResponse.model_rebuild()
