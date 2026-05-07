"""
Match Scoring Engine using Machine Learning.
Predicts how much a specific traveler profile will enjoy a specific attraction.
Uses a Random Forest Classifier trained on synthetic interaction data.
"""
import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from config import ML_MODELS_DIR, RANDOM_STATE
from ml.profiler import profiler

class MatchScoringEngine:
    def __init__(self):
        self.models_dir = ML_MODELS_DIR
        os.makedirs(self.models_dir, exist_ok=True)
        self.model_path = os.path.join(self.models_dir, "match_scorer_rf.joblib")
        self.scaler_path = os.path.join(self.models_dir, "match_scorer_scaler.joblib")
        
        self.model = None
        self.scaler = None
        
        self.feature_columns = [
            # Interaction Features (Differences)
            'budget_diff', 'crowd_diff', 'intensity_diff', 
            'cultural_diff', 'nightlife_diff', 'adventure_diff',
            # User Features
            'u_pace', 'u_budget', 'u_crowd', 'u_culture', 'u_adventure', 'u_nightlife',
            # Attraction Features
            'a_cost', 'a_crowd', 'a_intensity', 'a_culture', 'a_adventure', 'a_nightlife'
        ]
        
        self.load_models()

    def _generate_synthetic_interactions(self, n_samples=5000):
        """Generates synthetic dataset of users rating attractions."""
        np.random.seed(RANDOM_STATE)
        
        data = []
        for _ in range(n_samples):
            # Generate random user profile (1-5 scale)
            u_pace = np.random.uniform(1, 5)
            u_budget = np.random.uniform(1, 5)
            u_crowd = np.random.uniform(1, 5)
            u_culture = np.random.uniform(1, 5)
            u_adventure = np.random.uniform(1, 5)
            u_nightlife = np.random.uniform(1, 5)
            
            # Generate random attraction profile (1-5 scale, except cost which we normalize)
            a_cost = np.random.uniform(1, 5) # Normalized cost indicator
            a_crowd = np.random.uniform(1, 5)
            a_intensity = np.random.uniform(1, 5)
            a_culture = np.random.uniform(1, 5)
            a_adventure = np.random.uniform(1, 5)
            a_nightlife = np.random.uniform(1, 5)
            
            # Calculate absolute differences (lower difference = better match)
            budget_diff = abs(u_budget - a_cost)
            crowd_diff = abs(u_crowd - a_crowd)
            intensity_diff = abs(u_pace - a_intensity)
            cultural_diff = abs(u_culture - a_culture)
            nightlife_diff = abs(u_nightlife - a_nightlife)
            adventure_diff = abs(u_adventure - a_adventure)
            
            # Synthetic Logic: Create a label (1=Enjoyed, 0=Not Enjoyed) based on differences
            # If total mismatch is low, user enjoyed it.
            total_mismatch = (budget_diff*1.5 + crowd_diff + intensity_diff + 
                              cultural_diff*1.2 + nightlife_diff + adventure_diff)
            
            # Add some randomness to simulate real human behavior
            noise = np.random.normal(0, 1.0)
            
            # Threshold for enjoying
            enjoyed = 1 if (total_mismatch + noise) < 10.0 else 0
            
            row = [
                budget_diff, crowd_diff, intensity_diff, cultural_diff, nightlife_diff, adventure_diff,
                u_pace, u_budget, u_crowd, u_culture, u_adventure, u_nightlife,
                a_cost, a_crowd, a_intensity, a_culture, a_adventure, a_nightlife,
                enjoyed
            ]
            data.append(row)
            
        columns = self.feature_columns + ['enjoyed']
        return pd.DataFrame(data, columns=columns)

    def train(self):
        """Trains the Random Forest Match model."""
        print("Training Match Scoring Engine...")
        df = self._generate_synthetic_interactions()
        
        X = df[self.feature_columns]
        y = df['enjoyed']
        
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Use Random Forest for non-linear interactions
        self.model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=RANDOM_STATE)
        self.model.fit(X_scaled, y)
        
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        print("Match Scoring Engine trained and saved.")

    def load_models(self):
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
        else:
            self.train()

    def _normalize_cost(self, cost_inr: float) -> float:
        """Converts raw INR cost to a 1-5 scale for the model."""
        if cost_inr <= 200: return 1.0
        if cost_inr <= 1000: return 2.0
        if cost_inr <= 2500: return 3.0
        if cost_inr <= 5000: return 4.0
        return 5.0

    def calculate_match_score(self, user_profile: dict, attraction: dict) -> dict:
        """
        Calculates match probability (0.0 to 1.0) and generates an explainable AI reason.
        """
        # Extract features
        u_pace = user_profile.get('travel_pace', 3.0)
        u_budget = user_profile.get('budget_per_day', 3.0)
        u_crowd = user_profile.get('crowd_tolerance', 3.0)
        u_culture = user_profile.get('cultural_curiosity', 3.0)
        u_adventure = user_profile.get('adventure_appetite', 3.0)
        u_nightlife = user_profile.get('nightlife_interest', 3.0)
        
        a_cost = self._normalize_cost(attraction.get('cost_estimate_inr', 0))
        a_crowd = attraction.get('crowd_density', 3.0)
        a_intensity = attraction.get('physical_intensity', 3.0)
        a_culture = attraction.get('cultural_depth', 3.0)
        a_adventure = attraction.get('adventure_level', 3.0)
        a_nightlife = attraction.get('nightlife_score', 3.0)
        
        # Calculate differences
        features = [
            abs(u_budget - a_cost),
            abs(u_crowd - a_crowd),
            abs(u_pace - a_intensity),
            abs(u_culture - a_culture),
            abs(u_nightlife - a_nightlife),
            abs(u_adventure - a_adventure),
            u_pace, u_budget, u_crowd, u_culture, u_adventure, u_nightlife,
            a_cost, a_crowd, a_intensity, a_culture, a_adventure, a_nightlife
        ]
        
        # Predict probability of class 1 (enjoyed)
        X_scaled = self.scaler.transform([features])
        prob = self.model.predict_proba(X_scaled)[0][1]
        
        # Generate Explainable AI reason based on the smallest difference (best alignment)
        diffs = {
            "budget": abs(u_budget - a_cost),
            "crowd preference": abs(u_crowd - a_crowd),
            "activity pace": abs(u_pace - a_intensity),
            "cultural interest": abs(u_culture - a_culture),
            "nightlife preference": abs(u_nightlife - a_nightlife),
            "adventure level": abs(u_adventure - a_adventure)
        }
        
        best_match_feature = min(diffs, key=diffs.get)
        reason = f"Excellent match for your {best_match_feature}."
        
        if diffs[best_match_feature] > 2.0:
            reason = "A unique experience outside your usual preferences."
            
        # Hard constraints overriding ML
        if u_budget < 2.0 and a_cost > 4.0:
            prob *= 0.5 # Penalty for being way over budget
            reason = "Warning: This attraction may be over your preferred budget."

        return {
            "score": float(prob),
            "reason": reason
        }

match_scorer = MatchScoringEngine()
