import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

class Config:
    """Base application configuration class loaded from environment variables."""
    SECRET_KEY = os.getenv("SECRET_KEY", "default-dev-secret-key-please-change-in-production")
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = os.getenv("FLASK_ENV") == "development"
    PORT = int(os.getenv("PORT", 5000))
    
    # Optional TMDB API Key for retrieving movie posters
    TMDB_API_KEY = os.getenv("TMDB_API_KEY", "").strip()
    
    # Paths for dataset and model pickle files
    DATASET_DIR = BASE_DIR / "dataset"
    DATASET_FILE = DATASET_DIR / "tmdb_5000_movies.csv"
    
    MOVIES_PKL = BASE_DIR / "movies.pkl"
    SIMILARITY_PKL = BASE_DIR / "similarity.pkl"
    TFIDF_PKL = BASE_DIR / "tfidf_vectorizer.pkl"
    
    # Recommendation Configuration
    TOP_N_RECOMMENDATIONS = 5
