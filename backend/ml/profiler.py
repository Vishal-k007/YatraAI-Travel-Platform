"""
Traveler Profiling Engine.
Uses K-Means clustering to classify users into 5 travel archetypes based on 15 personality traits.
"""
import os
import joblib
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from config import ML_MODELS_DIR, N_CLUSTERS, RANDOM_STATE

class TravelerProfiler:
    def __init__(self):
        self.models_dir = ML_MODELS_DIR
        os.makedirs(self.models_dir, exist_ok=True)
        self.model_path = os.path.join(self.models_dir, "kmeans_profiler.joblib")
        self.scaler_path = os.path.join(self.models_dir, "profiler_scaler.joblib")
        self.pca_path = os.path.join(self.models_dir, "profiler_pca.joblib")
        
        self.model = None
        self.scaler = None
        self.pca = None
        
        # Archetype mapping
        self.archetypes = {
            0: {
                "name": "High-Energy Social Explorer",
                "description": "You love fast-paced travel, bustling nightlife, and social settings. You're an adventurous foodie who seeks out vibrant environments.",
                "traits": ["High Energy", "Social", "Nightlife", "Fast Pace"]
            },
            1: {
                "name": "Budget Nature Seeker",
                "description": "You prefer slow, affordable travel immersed in nature. You're comfortable with basic amenities and love outdoor adventures.",
                "traits": ["Budget", "Nature", "Slow Pace", "Outdoors"]
            },
            2: {
                "name": "Cultural Depth Traveler",
                "description": "You seek authentic local experiences, historical depth, and cultural immersion over typical tourist traps.",
                "traits": ["Culture", "History", "Local", "Curious"]
            },
            3: {
                "name": "Comfort-Oriented Relaxer",
                "description": "You travel to unwind. You prefer luxury, comfortable climates, minimal physical exertion, and well-planned itineraries.",
                "traits": ["Comfort", "Relaxation", "Luxury", "Planned"]
            },
            4: {
                "name": "Adventure-Focused Wanderer",
                "description": "You are highly adventurous, physically active, and spontaneous. You thrive in intense, thrilling environments.",
                "traits": ["Adventure", "Active", "Spontaneous", "Thrill"]
            }
        }
        
        self.load_models()

    def _generate_synthetic_training_data(self, n_samples=1000):
        """Generates synthetic survey data to train the initial K-Means model."""
        np.random.seed(RANDOM_STATE)
        
        # Define 5 distinct cluster centers manually to ensure clear separation initially
        centers = [
            # 1. High-Energy Social (High pace, crowds, nightlife, social)
            [4.5, 3.5, 4.5, 4.0, 3.0, 3.5, 3.0, 3.5, 4.8, 1.5, 3.0, 4.5, 4.0, 3.5, 3.0],
            # 2. Budget Nature (Slow, budget, low crowds, active)
            [2.0, 1.5, 1.5, 2.5, 3.0, 4.0, 4.0, 4.5, 1.0, 3.0, 1.0, 2.0, 3.0, 4.5, 4.0],
            # 3. Cultural Depth (Moderate pace, high culture/local)
            [3.0, 3.0, 3.0, 4.0, 4.8, 2.5, 3.0, 4.0, 2.0, 3.0, 2.5, 3.0, 2.5, 3.5, 4.8],
            # 4. Comfort Relaxer (Slow, luxury, low physical)
            [1.5, 4.8, 2.0, 2.0, 2.5, 1.0, 2.0, 2.5, 1.5, 4.8, 4.8, 3.0, 1.5, 1.5, 2.0],
            # 5. Adventure Wanderer (Fast, high adventure, spontaneous)
            [4.0, 2.5, 2.5, 3.5, 3.0, 4.8, 4.5, 3.5, 2.5, 1.0, 1.5, 2.5, 4.8, 4.5, 3.5]
        ]
        
        data = []
        for i in range(n_samples):
            # Pick a random cluster center and add some noise
            cluster_idx = np.random.randint(0, 5)
            center = centers[cluster_idx]
            noise = np.random.normal(0, 0.5, 15)
            sample = np.clip(np.array(center) + noise, 1.0, 5.0)
            data.append(sample)
            
        columns = [
            'travel_pace', 'budget_per_day', 'crowd_tolerance', 'food_adventurousness',
            'cultural_curiosity', 'adventure_appetite', 'climate_tolerance', 'photography_interest',
            'nightlife_interest', 'relaxation_preference', 'luxury_preference', 'social_preference',
            'planning_spontaneity', 'walking_tolerance', 'local_experience'
        ]
        return pd.DataFrame(data, columns=columns)

    def train(self):
        """Trains the K-Means model on synthetic data."""
        print("Training Traveler Profiler model...")
        df = self._generate_synthetic_training_data()
        
        self.scaler = StandardScaler()
        scaled_data = self.scaler.fit_transform(df)
        
        self.model = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_STATE, n_init=10)
        self.model.fit(scaled_data)
        
        # PCA for 2D visualization
        self.pca = PCA(n_components=2)
        self.pca.fit(scaled_data)
        
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        joblib.dump(self.pca, self.pca_path)
        print("Traveler Profiler trained and saved.")

    def load_models(self):
        """Loads pre-trained models or trains if they don't exist."""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            if os.path.exists(self.pca_path):
                self.pca = joblib.load(self.pca_path)
        else:
            self.train()

    def predict_profile(self, user_answers: dict) -> dict:
        """
        Takes 15 quiz answers (1-5 scale) and returns the traveler profile.
        """
        # Ensure correct order
        features = [
            'travel_pace', 'budget_per_day', 'crowd_tolerance', 'food_adventurousness',
            'cultural_curiosity', 'adventure_appetite', 'climate_tolerance', 'photography_interest',
            'nightlife_interest', 'relaxation_preference', 'luxury_preference', 'social_preference',
            'planning_spontaneity', 'walking_tolerance', 'local_experience'
        ]
        
        input_data = [user_answers.get(f, 3.0) for f in features]
        
        # Transform and predict
        scaled_input = self.scaler.transform([input_data])
        cluster_id = int(self.model.predict(scaled_input)[0])
        
        # Get distances to cluster centers to calculate a confidence score or primary traits
        distances = self.model.transform(scaled_input)[0]
        
        # Project to 2D for visualization
        if self.pca:
            pca_coords = self.pca.transform(scaled_input)[0]
            pca_dict = {"x": float(pca_coords[0]), "y": float(pca_coords[1])}
        else:
            pca_dict = {"x": 0.0, "y": 0.0}
            
        archetype_info = self.archetypes[cluster_id]
        
        return {
            "cluster_id": cluster_id,
            "archetype": archetype_info["name"],
            "archetype_explanation": archetype_info["description"],
            "pca_coordinates": pca_dict,
            "traits": archetype_info["traits"]
        }

profiler = TravelerProfiler()
