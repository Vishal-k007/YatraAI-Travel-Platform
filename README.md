# AI-Powered Personalized Travel Itinerary Platform for Indian Destinations

![YatraAI Banner](https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&q=80&w=2071&ixlib=rb-4.0.3)

## Project Vision
YatraAI is an intelligent travel platform that generates highly personalized, behavior-aware travel itineraries for Indian destinations (Goa, Jaipur, Manali). Instead of generic "Top 10" lists, it optimizes for *experience alignment* using Machine Learning.

## Core Architecture

The system consists of 4 intelligent layers:
1. **Traveler Profiling Engine**: Uses K-Means clustering to classify users into 5 archetypes based on a 15-question personality assessment.
2. **Attraction Intelligence Database**: A structured repository of 50+ real Indian attractions, each tagged with 20+ ML-ready dimensions.
3. **Match Scoring Engine**: A Random Forest Classifier that predicts compatibility between a specific user profile and an attraction, providing Explainable AI reasons.
4. **Route & Energy Optimizer**: A constraint optimization algorithm that builds geographically sensible, energy-balanced daily itineraries.

## Tech Stack
- **Frontend**: React.js, TypeScript, Vite, Tailwind CSS, Framer Motion, Recharts
- **Backend**: Python, FastAPI, SQLAlchemy, SQLite (for portability)
- **Machine Learning**: Scikit-learn, Pandas, NumPy
- **Authentication**: JWT, bcrypt

## Repository Structure
```
.
├── backend/                  # FastAPI Application & ML Pipelines
│   ├── ml/                   # Machine Learning Models & Logic
│   ├── routes/               # API Endpoints
│   ├── models.py             # SQLAlchemy Database Schema
│   ├── schemas.py            # Pydantic Validation Schemas
│   ├── run.py                # Server Entrypoint
│   └── seed_data.py          # Attraction Database Seeder
├── frontend/                 # React Application (Coming Next)
└── README.md
```

## Setup Instructions

### 1. Backend Setup
```bash
cd backend

# Optional: Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run initial setup (creates DB, runs ML training on synthetic data)
python run.py --setup

# Start server
python run.py
```
The backend API will be available at `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The frontend UI will be available at `http://localhost:5173`.
