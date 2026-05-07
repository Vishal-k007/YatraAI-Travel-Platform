"""
Main FastAPI Application Entrypoint.
Configures CORS, integrates routes, and initializes the database.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, init_db
from config import APP_NAME, APP_VERSION, DEBUG, CORS_ORIGINS
from ml.profiler import profiler
from ml.match_scorer import match_scorer

# Import routers
from routes import auth, profile, attractions, itineraries, analytics

# Initialize database
init_db()

# Initialize ML Models in background (or ensure they exist)
profiler.load_models()
match_scorer.load_models()

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    debug=DEBUG,
    description="AI-Powered Personalized Travel Itinerary Platform for Indian Destinations"
)

# Configure CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(profile.router, prefix="/api/profile", tags=["Traveler Profile"])
app.include_router(attractions.router, prefix="/api/attractions", tags=["Attractions"])
app.include_router(itineraries.router, prefix="/api/itineraries", tags=["Itineraries"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

@app.get("/", tags=["Health"])
def health_check():
    """Root endpoint for health checks."""
    return {
        "status": "online",
        "app": APP_NAME,
        "version": APP_VERSION,
        "message": "Welcome to the YatraAI API"
    }

# Run with: uvicorn main:app --reload
