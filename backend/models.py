"""
SQLAlchemy ORM Models for the Travel Itinerary Platform.
Defines all database tables: Users, TravelerProfiles, Attractions,
Itineraries, ItineraryDays, ItinerarySlots, and Favorites.
"""
import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime,
    ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    """User account model for authentication and profile management."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    profile = relationship("TravelerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    itineraries = relationship("Itinerary", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")


class TravelerProfile(Base):
    """
    Stores the traveler's personality quiz answers and computed archetype.
    Each user has exactly one profile generated from the 15-question quiz.
    """
    __tablename__ = "traveler_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # --- 15 Quiz Dimensions (each scored 1-5) ---
    travel_pace = Column(Float, nullable=False)          # 1=slow, 5=fast
    budget_per_day = Column(Float, nullable=False)       # 1=budget, 5=luxury
    crowd_tolerance = Column(Float, nullable=False)      # 1=avoids crowds, 5=loves crowds
    food_adventurousness = Column(Float, nullable=False)  # 1=familiar, 5=adventurous
    cultural_curiosity = Column(Float, nullable=False)   # 1=low, 5=high
    adventure_appetite = Column(Float, nullable=False)   # 1=none, 5=extreme
    climate_tolerance = Column(Float, nullable=False)    # 1=sensitive, 5=any climate
    photography_interest = Column(Float, nullable=False) # 1=none, 5=passionate
    nightlife_interest = Column(Float, nullable=False)   # 1=none, 5=loves nightlife
    relaxation_preference = Column(Float, nullable=False) # 1=always active, 5=needs rest
    luxury_preference = Column(Float, nullable=False)    # 1=basic, 5=luxury only
    social_preference = Column(Float, nullable=False)    # 1=solo, 5=very social
    planning_spontaneity = Column(Float, nullable=False) # 1=strict plans, 5=spontaneous
    walking_tolerance = Column(Float, nullable=False)    # 1=minimal, 5=loves walking
    local_experience = Column(Float, nullable=False)     # 1=tourist spots, 5=local hidden gems

    # --- Computed Fields ---
    archetype = Column(String(100), nullable=True)       # e.g., "High-Energy Social Explorer"
    cluster_id = Column(Integer, nullable=True)          # K-Means cluster assignment
    archetype_explanation = Column(Text, nullable=True)  # Why user belongs to this cluster
    archetype_scores = Column(JSON, nullable=True)       # Detailed dimension scores for radar chart
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="profile")


class Attraction(Base):
    """
    Represents a tourist attraction with rich metadata for ML matching.
    Contains 50-80 real Indian attractions across Goa, Jaipur, and Manali.
    """
    __tablename__ = "attractions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    city = Column(String(50), nullable=False, index=True)
    category = Column(String(100), nullable=False)       # Beach, Fort, Temple, etc.
    description = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # --- Visit Metadata ---
    avg_visit_duration_hours = Column(Float, nullable=False)  # in hours
    cost_estimate_inr = Column(Float, nullable=False)         # in INR
    best_visiting_time = Column(String(50), nullable=False)   # Morning, Afternoon, Evening, Night, Any

    # --- Rich Media and Details ---
    image_urls = Column(JSON, nullable=True)
    reviews = Column(JSON, nullable=True)
    cost_breakdown = Column(JSON, nullable=True)

    # --- Scoring Dimensions (1-5 scale) ---
    crowd_density = Column(Float, nullable=False)        # 1=empty, 5=very crowded
    physical_intensity = Column(Float, nullable=False)   # 1=easy, 5=very strenuous
    photography_score = Column(Float, nullable=False)    # 1=nothing special, 5=incredible
    food_availability = Column(Float, nullable=False)    # 1=none, 5=excellent food scene
    family_friendliness = Column(Float, nullable=False)  # 1=not suitable, 5=very family friendly
    adventure_level = Column(Float, nullable=False)      # 1=none, 5=extreme adventure
    cultural_depth = Column(Float, nullable=False)       # 1=none, 5=rich cultural significance
    nightlife_score = Column(Float, nullable=False)      # 1=none, 5=vibrant nightlife
    weather_sensitivity = Column(Float, nullable=False)  # 1=indoor/any weather, 5=very weather dependent
    is_indoor = Column(Boolean, default=False)           # True if primarily indoor

    # --- Recommended archetypes (JSON list of archetype names) ---
    recommended_archetypes = Column(JSON, nullable=True)

    # Relationships
    favorites = relationship("Favorite", back_populates="attraction", cascade="all, delete-orphan")


class Itinerary(Base):
    """
    A generated travel itinerary for a user visiting a specific city.
    Contains multiple days, each with time-slotted activities.
    """
    __tablename__ = "itineraries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    city = Column(String(50), nullable=False)
    num_days = Column(Integer, nullable=False)
    total_budget_inr = Column(Float, nullable=True)
    title = Column(String(200), nullable=True)

    # --- Computed Metadata ---
    total_estimated_cost = Column(Float, nullable=True)
    total_attractions = Column(Integer, nullable=True)
    avg_daily_energy = Column(Float, nullable=True)
    match_score = Column(Float, nullable=True)            # Overall recommendation confidence

    # --- Itinerary Data (full JSON for frontend) ---
    itinerary_data = Column(JSON, nullable=True)          # Complete structured itinerary
    recommendations_explanation = Column(JSON, nullable=True)  # Why each attraction was picked

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="itineraries")
    days = relationship("ItineraryDay", back_populates="itinerary", cascade="all, delete-orphan")


class ItineraryDay(Base):
    """Represents a single day within an itinerary."""
    __tablename__ = "itinerary_days"

    id = Column(Integer, primary_key=True, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id"), nullable=False)
    day_number = Column(Integer, nullable=False)
    date_label = Column(String(50), nullable=True)       # e.g., "Day 1 - Monday"
    total_energy = Column(Float, nullable=True)           # Energy utilization for the day
    total_cost = Column(Float, nullable=True)             # Estimated cost for the day
    total_travel_time_mins = Column(Float, nullable=True) # Total travel time in minutes
    theme = Column(String(200), nullable=True)            # e.g., "Cultural Heritage & Markets"

    # Relationships
    itinerary = relationship("Itinerary", back_populates="days")
    slots = relationship("ItinerarySlot", back_populates="day", cascade="all, delete-orphan")


class ItinerarySlot(Base):
    """A single time slot within a day (an activity or break)."""
    __tablename__ = "itinerary_slots"

    id = Column(Integer, primary_key=True, index=True)
    day_id = Column(Integer, ForeignKey("itinerary_days.id"), nullable=False)
    slot_type = Column(String(50), nullable=False)       # "attraction", "lunch", "rest", "travel", "dinner"
    time_label = Column(String(50), nullable=False)      # e.g., "09:00 - 11:00"
    period = Column(String(20), nullable=False)          # "morning", "afternoon", "evening", "night"
    attraction_id = Column(Integer, ForeignKey("attractions.id"), nullable=True)
    attraction_name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    duration_hours = Column(Float, nullable=True)
    estimated_cost = Column(Float, nullable=True)
    energy_level = Column(Float, nullable=True)          # Energy required (1-5)
    travel_time_mins = Column(Float, nullable=True)      # Travel time from previous slot
    recommendation_reason = Column(Text, nullable=True)  # Explainable AI reason
    order_index = Column(Integer, nullable=False)

    # Relationships
    day = relationship("ItineraryDay", back_populates="slots")


class Favorite(Base):
    """User's favorite/bookmarked attractions."""
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    attraction_id = Column(Integer, ForeignKey("attractions.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="favorites")
    attraction = relationship("Attraction", back_populates="favorites")
