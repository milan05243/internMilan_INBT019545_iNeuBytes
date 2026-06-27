import pickle
import logging
from pathlib import Path
from config import Config

# Initialize logger
logger = logging.getLogger(__name__)

# Cache for loaded model artifacts to prevent repeated disk reads
_movies_df = None
_similarity_matrix = None
_tfidf_vectorizer = None

def load_model_artifacts():
    """Load model pickles from disk if they are not already loaded into cache."""
    global _movies_df, _similarity_matrix, _tfidf_vectorizer
    
    if _movies_df is not None and _similarity_matrix is not None:
        return True

    movies_path = Path(Config.MOVIES_PKL)
    similarity_path = Path(Config.SIMILARITY_PKL)
    tfidf_path = Path(Config.TFIDF_PKL)

    # Check if files exist
    if not (movies_path.exists() and similarity_path.exists() and tfidf_path.exists()):
        logger.error("Model artifacts not found. Please run train_model.py first.")
        return False

    try:
        logger.info("Loading model artifacts from pickles...")
        with open(movies_path, 'rb') as f:
            _movies_df = pickle.load(f)
            
        with open(similarity_path, 'rb') as f:
            _similarity_matrix = pickle.load(f)
            
        with open(tfidf_path, 'rb') as f:
            _tfidf_vectorizer = pickle.load(f)
            
        logger.info("Successfully loaded all model artifacts.")
        return True
    except Exception as e:
        logger.error(f"Error loading model artifacts: {e}", exc_info=True)
        return False

def get_autocomplete_suggestions(query, limit=10):
    """
    Search for movies matching a query substring and return suggestions.
    Matches are case-insensitive and check for occurrences anywhere in the title.
    """
    if not load_model_artifacts() or not query:
        return []
    
    query_clean = query.strip().lower()
    
    # Filter movies where query is a substring of the title
    matches = _movies_df[_movies_df['title_lower'].str.contains(query_clean, na=False)]
    
    # Sort matching titles: first those that start with the query, then others by popularity
    starts_with = matches[matches['title_lower'].str.startswith(query_clean)]
    contains_only = matches[~matches['title_lower'].str.startswith(query_clean)]
    
    sorted_matches = pd_concat_helper(starts_with.sort_values(by='popularity', ascending=False),
                                      contains_only.sort_values(by='popularity', ascending=False))
    
    # Return top N movie titles
    return sorted_matches['title'].head(limit).tolist()

def pd_concat_helper(df1, df2):
    """Concatenate two pandas dataframes safely."""
    import pandas as pd
    return pd.concat([df1, df2])

def get_recommendations(movie_title):
    """
    Given a movie title, return the top N similar movies.
    Performs case-insensitive lookup.
    """
    if not load_model_artifacts():
        raise RuntimeError("Model artifacts are not loaded.")

    title_clean = movie_title.strip().lower()
    
    # Find matching movie in the dataframe
    movie_row = _movies_df[_movies_df['title_lower'] == title_clean]
    
    if movie_row.empty:
        # Try a partial match if exact match is not found
        partial_matches = _movies_df[_movies_df['title_lower'].str.contains(title_clean, na=False)]
        if not partial_matches.empty:
            movie_row = partial_matches.iloc[[0]]
            logger.info(f"Exact match for '{movie_title}' not found. Using partial match: '{movie_row['title'].values[0]}'")
        else:
            logger.warning(f"Movie '{movie_title}' not found in dataset.")
            return None

    # Get index of the matched movie
    movie_idx = movie_row.index[0]
    movie_data = movie_row.iloc[0]
    
    # Fetch similarity scores for this movie
    similarity_scores = list(enumerate(_similarity_matrix[movie_idx]))
    
    # Sort similarity scores descending (exclude the movie itself, which is at index movie_idx)
    sorted_scores = sorted(
        [(idx, score) for idx, score in similarity_scores if idx != movie_idx],
        key=lambda x: x[1],
        reverse=True
    )
    
    # Get top N recommended movie indices
    top_n = Config.TOP_N_RECOMMENDATIONS
    recommended_indices = [idx for idx, score in sorted_scores[:top_n]]
    
    # Extract metadata for recommendations
    recommendations = []
    for idx in recommended_indices:
        row = _movies_df.iloc[idx]
        recommendations.append({
            "id": int(row['id']),
            "title": row['title'],
            "genres": row['genres_list'],
            "release_year": row['release_year'],
            "rating": float(row['vote_average']),
            "popularity": float(row['popularity'])
        })
        
    return {
        "searched_movie": {
            "id": int(movie_data['id']),
            "title": movie_data['title'],
            "genres": movie_data['genres_list'],
            "release_year": movie_data['release_year'],
            "rating": float(movie_data['vote_average'])
        },
        "recommendations": recommendations
    }

def get_featured_movies(limit=6):
    """
    Retrieve curated lists for the homepage feed:
    - Popular: top movies by popularity score.
    - Top Rated (Trending): top movies by vote_average with at least 150 votes.
    - Recently Released: movies sorted by release year descending with high popularity.
    """
    if not load_model_artifacts():
        return {"popular": [], "trending": [], "recent": []}

    try:
        # 1. Popular Movies
        popular_df = _movies_df.sort_values(by='popularity', ascending=False).head(limit)
        
        # 2. Trending Movies (defined as high vote average with popularity filter)
        # Note: raw dataset doesn't have vote_count in the processed pkl directly if we didn't save it.
        # But we saved popularity and vote_average. So we sort by vote_average among popular movies.
        trending_df = _movies_df[_movies_df['popularity'] > _movies_df['popularity'].median()]
        trending_df = trending_df.sort_values(by='vote_average', ascending=False).head(limit)
        
        # 3. Recently Released Movies
        # Filter out "N/A" years, convert to numeric for sorting, and sort by year and popularity
        recent_df = _movies_df[_movies_df['release_year'] != "N/A"].copy()
        recent_df['release_year_numeric'] = recent_df['release_year'].astype(int)
        recent_df = recent_df.sort_values(by=['release_year_numeric', 'popularity'], ascending=[False, False]).head(limit)
        
        # Helper to convert dataframe slice to dictionary list
        def to_dict_list(df):
            records = []
            for _, row in df.iterrows():
                records.append({
                    "id": int(row['id']),
                    "title": row['title'],
                    "genres": row['genres_list'],
                    "release_year": row['release_year'],
                    "rating": float(row['vote_average']),
                    "popularity": float(row['popularity'])
                })
            return records

        return {
            "popular": to_dict_list(popular_df),
            "trending": to_dict_list(trending_df),
            "recent": to_dict_list(recent_df)
        }
    except Exception as e:
        logger.error(f"Error fetching featured movies: {e}", exc_info=True)
        return {"popular": [], "trending": [], "recent": []}
