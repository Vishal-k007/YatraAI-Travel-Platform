"""
Configuration module for the Travel Itinerary Platform.
Manages environment variables and application settings.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Database Configuration ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./travel_platform.db")

# --- JWT Configuration ---
SECRET_KEY = os.getenv("SECRET_KEY", "yatra-ai-super-secret-key-change-in-production-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours

# --- Application Configuration ---
APP_NAME = "YatraAI - Smart Travel Planner"
APP_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

# --- ML Configuration ---
ML_MODELS_DIR = os.path.join(os.path.dirname(__file__), "ml", "models")
N_CLUSTERS = 5  # Number of traveler archetypes
RANDOM_STATE = 42

# --- Supported Cities ---
SUPPORTED_CITIES = ["Goa", "Jaipur", "Manali"]
