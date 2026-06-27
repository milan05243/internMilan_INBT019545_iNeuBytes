import os
import urllib.request
import pandas as pd
import numpy as np
import pickle
import json
import ast
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Constants
DATASET_URL = "https://raw.githubusercontent.com/fenago/datasets/refs/heads/main/tmdb_5000_movies.csv"
BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "dataset"
DATASET_FILE = DATASET_DIR / "tmdb_5000_movies.csv"

# Output Pickle Files
MOVIES_PKL = BASE_DIR / "movies.pkl"
SIMILARITY_PKL = BASE_DIR / "similarity.pkl"
TFIDF_PKL = BASE_DIR / "tfidf_vectorizer.pkl"

def download_dataset():
    """Download the TMDB 5000 Movies dataset if not already present."""
    if not DATASET_DIR.exists():
        DATASET_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {DATASET_DIR}")

    if not DATASET_FILE.exists():
        print(f"Downloading dataset from {DATASET_URL}...")
        try:
            # Add User-Agent header to avoid potential blocks
            req = urllib.request.Request(
                DATASET_URL, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req) as response, open(DATASET_FILE, 'wb') as out_file:
                out_file.write(response.read())
            print(f"Successfully downloaded dataset to {DATASET_FILE}")
        except Exception as e:
            print(f"Error downloading dataset: {e}")
            raise e
    else:
        print("Dataset already exists locally.")

def parse_json_column(column_val):
    """Parse JSON strings (genres, keywords) into a list of name strings."""
    if not isinstance(column_val, str) or pd.isna(column_val):
        return []
    try:
        # Attempt to load using standard json
        items = json.loads(column_val)
        return [item['name'] for item in items]
    except Exception:
        try:
            # Fallback to ast.literal_eval for single quotes or malformed JSON
            items = ast.literal_eval(column_val)
            return [item['name'] for item in items]
        except Exception:
            return []

def extract_year(release_date):
    """Extract release year from the release_date string (YYYY-MM-DD)."""
    if not isinstance(release_date, str) or pd.isna(release_date) or len(release_date) < 4:
        return "N/A"
    return release_date.split('-')[0]

def preprocess_data(df):
    """Clean the raw dataframe and extract columns for the model."""
    print("Preprocessing raw movies dataset...")
    
    # 1. Fill missing values
    df['overview'] = df['overview'].fillna('')
    df['title'] = df['title'].fillna('Unknown Title')
    
    # 2. Parse JSON columns (genres, keywords)
    df['genres_list'] = df['genres'].apply(parse_json_column)
    df['keywords_list'] = df['keywords'].apply(parse_json_column)
    
    # 3. Format release year
    df['release_year'] = df['release_date'].apply(extract_year)
    
    # 4. Clean genres and keywords by stripping spaces (e.g. "Science Fiction" -> "sciencefiction")
    # This prevents the TF-IDF vectorizer from splitting them into separate words.
    df['cleaned_genres'] = df['genres_list'].apply(lambda x: [g.replace(" ", "").lower() for g in x])
    df['cleaned_keywords'] = df['keywords_list'].apply(lambda x: [k.replace(" ", "").lower() for k in x])
    
    # 5. Create final 'tags' metadata feature combining overview, genres, and keywords
    df['tags'] = df.apply(
        lambda row: f"{row['overview']} "
                    f"{' '.join(row['cleaned_genres'])} "
                    f"{' '.join(row['cleaned_keywords'])}", 
        axis=1
    )
    
    # 6. Normalize tags text (strip whitespace, lowercase)
    df['tags'] = df['tags'].apply(lambda x: x.strip().lower())
    
    # Keep only the necessary columns for pickle sizes and app speed
    processed_df = df[[
        'id', 'title', 'genres_list', 'release_year', 
        'vote_average', 'popularity', 'tags'
    ]].copy()
    
    # Store clean title for lookups
    processed_df['title_lower'] = processed_df['title'].str.strip().str.lower()
    
    print(f"Preprocessed {len(processed_df)} movies successfully.")
    return processed_df

def train_recommender(df):
    """Train the TF-IDF Vectorizer and calculate the Cosine Similarity matrix."""
    print("Vectorizing movie tags using TF-IDF...")
    # Initialize TF-IDF Vectorizer with standard stop words
    tfidf = TfidfVectorizer(max_features=5000, stop_words='english')
    
    # Fit and transform the movie tags
    tfidf_matrix = tfidf.fit_transform(df['tags'])
    print(f"TF-IDF matrix shape: {tfidf_matrix.shape}")
    
    print("Calculating cosine similarity matrix...")
    # Calculate pairwise cosine similarity (save as float32 to reduce pickle file size)
    similarity = cosine_similarity(tfidf_matrix).astype(np.float32)
    print(f"Similarity matrix shape: {similarity.shape}")
    
    # Save the vectorizer, processed movies DataFrame, and similarity matrix
    print("Pickling model artifacts...")
    
    with open(MOVIES_PKL, 'wb') as f:
        pickle.dump(df, f)
        print(f"Saved: {MOVIES_PKL} (Size: {MOVIES_PKL.stat().st_size / 1024 / 1024:.2f} MB)")
        
    with open(SIMILARITY_PKL, 'wb') as f:
        pickle.dump(similarity, f)
        print(f"Saved: {SIMILARITY_PKL} (Size: {SIMILARITY_PKL.stat().st_size / 1024 / 1024:.2f} MB)")
        
    with open(TFIDF_PKL, 'wb') as f:
        pickle.dump(tfidf, f)
        print(f"Saved: {TFIDF_PKL} (Size: {TFIDF_PKL.stat().st_size / 1024:.2f} KB)")
        
    print("Model training and pickling completed successfully!")

if __name__ == "__main__":
    try:
        download_dataset()
        raw_df = pd.read_csv(DATASET_FILE)
        processed_df = preprocess_data(raw_df)
        train_recommender(processed_df)
    except Exception as e:
        print(f"Training failed: {e}")
