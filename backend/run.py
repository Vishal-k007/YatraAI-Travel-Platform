"""
Utility script to run the backend and optionally seed the database.
"""
import uvicorn
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine, SessionLocal, init_db
from models import Base
from seed_data import seed_database
from ml.profiler import profiler
from ml.match_scorer import match_scorer

def setup():
    print("Initializing Database...")
    init_db()
    
    print("Seeding database...")
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
        
    print("Checking ML Models...")
    profiler.load_models()
    match_scorer.load_models()
    print("Setup Complete.")

if __name__ == "__main__":
    if "--setup" in sys.argv:
        setup()
    
    print("Starting FastAPI Server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
