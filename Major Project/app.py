import logging
from flask import Flask, request, jsonify, render_template
from config import Config
import recommender

# Initialize logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)
app.config.from_object(Config)

# Try loading model artifacts on startup
with app.app_context():
    logger.info("Initializing recommendation model artifacts on server startup...")
    success = recommender.load_model_artifacts()
    if success:
        logger.info("Model artifacts loaded successfully on startup.")
    else:
        logger.warning("Model artifacts could not be loaded. Please run train_model.py to generate pickle files.")

@app.route("/")
def index():
    """Render the homepage of the movie recommendation system."""
    return render_template("index.html")

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint indicating whether the application and models are active."""
    models_loaded = (
        recommender._movies_df is not None and 
        recommender._similarity_matrix is not None
    )
    return jsonify({
        "status": "healthy",
        "models_loaded": models_loaded,
        "config": {
            "environment": app.config["FLASK_ENV"],
            "top_n": app.config["TOP_N_RECOMMENDATIONS"],
            "tmdb_poster_api_enabled": bool(app.config["TMDB_API_KEY"])
        }
    }), 200

@app.route("/autocomplete", methods=["GET"])
def autocomplete():
    """
    Endpoint providing autocomplete suggestions for movie search.
    Query parameter: q (search term)
    """
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([]), 200
        
    try:
        suggestions = recommender.get_autocomplete_suggestions(query)
        return jsonify(suggestions), 200
    except Exception as e:
        logger.error(f"Autocomplete error: {e}", exc_info=True)
        return jsonify({"error": "Failed to generate suggestions"}), 500

@app.route("/movies/featured", methods=["GET"])
def featured_movies():
    """Endpoint returning lists of popular, trending, and recently released movies for the home feed."""
    try:
        featured = recommender.get_featured_movies()
        # Include API config info so the frontend knows if it should make direct TMDB calls
        response_data = {
            "featured": featured,
            "tmdb_api_key_configured": bool(app.config["TMDB_API_KEY"]),
            # We don't send the API key itself to the frontend to keep it secure.
            # The client will call a proxy or the frontend will fetch using a client-side key,
            # or in our case, if TMDB_API_KEY is configured, we can fetch on the frontend by
            # exposing a backend route or we can just safely send the key if it's a public key,
            # but to be secure, we can expose a proxy endpoint for posters on the backend so
            # the API key remains secret and server-side! Yes! This is extremely professional.
        }
        return jsonify(response_data), 200
    except Exception as e:
        logger.error(f"Error fetching featured movies: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch featured movies"}), 500

@app.route("/recommend", methods=["POST"])
def recommend():
    """
    REST API endpoint for movie recommendations.
    Expects JSON: { "movie_name": "Avatar" }
    Returns JSON containing the queried movie and a list of 5 recommendations.
    """
    # 1. Parse JSON input
    data = request.get_json(silent=True)
    if not data or "movie_name" not in data:
        return jsonify({"error": "Invalid request. Please provide 'movie_name' in JSON body."}), 400

    movie_name = data["movie_name"].strip()
    if not movie_name:
        return jsonify({"error": "Movie name cannot be empty."}), 400

    try:
        # Verify model artifacts are loaded
        if recommender._movies_df is None:
            # Try reloading in case they were generated post-startup
            loaded = recommender.load_model_artifacts()
            if not loaded:
                return jsonify({"error": "Recommendation model files are missing on server. Please train the model."}), 500

        # 2. Query recommendation system
        results = recommender.get_recommendations(movie_name)
        
        if not results:
            return jsonify({
                "error": f"Movie '{movie_name}' not found. Please check spelling or try another movie."
            }), 404
            
        return jsonify(results), 200

    except Exception as e:
        logger.error(f"Error generating recommendations for '{movie_name}': {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred while processing recommendations."}), 500

@app.route("/poster/<int:movie_id>", methods=["GET"])
def get_poster_path(movie_id):
    """
    Secure backend proxy to lookup TMDB poster URL using the server-side TMDB_API_KEY.
    Prevents leaking the API key to the frontend client.
    """
    api_key = app.config["TMDB_API_KEY"]
    if not api_key:
        return jsonify({"poster_path": None, "reason": "No TMDB_API_KEY configured"}), 200

    import requests
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            poster_path = data.get("poster_path")
            if poster_path:
                full_poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                return jsonify({"poster_url": full_poster_url}), 200
        
        logger.warning(f"Failed to fetch poster for movie ID {movie_id} from TMDB API: Status {response.status_code}")
        return jsonify({"poster_url": None}), 200
    except Exception as e:
        logger.error(f"Error fetching TMDB poster path: {e}")
        return jsonify({"poster_url": None, "error": str(e)}), 500

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors with structured JSON instead of browser default."""
    if request.path.startswith("/api/") or request.headers.get("Content-Type") == "application/json":
        return jsonify({"error": "Requested resource not found"}), 404
    return render_template("index.html")  # SPA fallback or simple template render

@app.errorhandler(500)
def internal_server_error(error):
    """Handle 500 errors with structured JSON."""
    return jsonify({"error": "An internal server error occurred"}), 500

if __name__ == "__main__":
    # Start the Flask app
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
