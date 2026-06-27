# CineMatch: AI Movie Recommendation System

CineMatch is a full-stack Machine Learning-based Movie Recommendation System designed as a major project for an Artificial Intelligence Internship. It leverages Content-Based Filtering algorithms to suggest top-5 similar movies based on a user's movie selection. The project features a modular Flask backend, a modern glassmorphism Bootstrap 5 frontend, and an offline ML training pipeline that parses the TMDB 5000 Movies Dataset.

---

##  Features

- **Content-Based ML Engine**: Utilizes TF-IDF vectorization and Cosine Similarity to find similar movies based on plot overviews, genres, and keywords.
- **Dynamic Autocomplete**: Real-time case-insensitive autocomplete suggestions while typing in the search bar.
- **Curated Home Feed**: Pre-loaded collections for **Popular**, **Trending**, and **Recently Released** movies on startup to keep the page engaging.
- **Interactive Glassmorphism UI**: Beautiful, fully responsive dark-theme design containing hover micro-animations and smooth transitions.
- **Secure Poster Integration**: Real-time movie posters via TMDB API. If the API key is missing, the system dynamically displays clean SVG-based gradient poster placeholders.
- **Robust REST API**: Modular routes, structured JSON responses, proper HTTP status codes, and global error handlers.
- **Production-Ready**: Configured for quick deployments on Render (Backend) and Vercel (Frontend).

---


##  Tech Stack

### Machine Learning
- **Python** (v3.8+)
- **Pandas** (Data cleaning and structural manipulation)
- **NumPy** (Numerical and array math)
- **Scikit-learn** (TF-IDF Vectorizer and Cosine Similarity computation)

### Backend (Flask Server)
- **Flask** (Micro web framework)
- **Python-dotenv** (Environment variable management)
- **Requests** (HTTP client for proxies)
- **Gunicorn** (WSGI HTTP server for production)

### Frontend (User Interface)
- **HTML5 & CSS3** (Semantic layout and styling)
- **Bootstrap 5** (Responsive layout system)
- **FontAwesome** (Icons)
- **JavaScript (Vanilla)** (DOM manipulation, autocomplete, and async API calls)

---


##  Installation & Setup

Follow these steps to run CineMatch locally on your machine:

### 1. Clone the Repository
```bash
git clone https://github.com/milan05243/internsMilan_INBT019545_iNeuBytes.git
cd "Major Project"
```

### 2. Set Up a Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and fill in the values:
```bash
cp .env.example .env
```
Open `.env` in a text editor:
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_development_secret_key
PORT=5000

# Optional TMDB API key for real movie posters
# Get a free key at https://www.themoviedb.org/documentation/api
TMDB_API_KEY=your_tmdb_api_key_here
```

### 5. Train the Machine Learning Model
Run the model training script. This script will automatically download the `tmdb_5000_movies.csv` file from a public source, preprocess it, calculate the cosine similarity matrix, and generate the required pickle files:
```bash
python train_model.py
```
After a successful run, verify that `movies.pkl`, `similarity.pkl`, and `tfidf_vectorizer.pkl` are generated in the root folder.

### 6. Run the Flask Server
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000` to interact with CineMatch.

---

## 🔌 API Documentation

All endpoints return properly structured JSON payloads.

### 1. GET `/health`
Returns the status of the server and whether the model pickle files are loaded into memory.
- **Request**: `GET /health`
- **Response Example (200 OK)**:
```json
{
  "status": "healthy",
  "models_loaded": true,
  "config": {
    "environment": "development",
    "top_n": 5,
    "tmdb_poster_api_enabled": true
  }
}
```

### 2. GET `/autocomplete`
Provides autocomplete list suggestions based on titles matching the query substring.
- **Request**: `GET /autocomplete?q=av`
- **Response Example (200 OK)**:
```json
[
  "Avatar",
  "Avengers: Age of Ultron",
  "The Avengers",
  "Avengers: Infinity War"
]
```

### 3. GET `/movies/featured`
Returns lists of popular, trending, and recently released movies for the home feed.
- **Request**: `GET /movies/featured`
- **Response Example (200 OK)**:
```json
{
  "featured": {
    "popular": [
      {
        "id": 19995,
        "title": "Avatar",
        "genres": ["Action", "Adventure", "Fantasy", "Science Fiction"],
        "release_year": "2009",
        "rating": 7.2,
        "popularity": 150.437577
      }
    ],
    "trending": [],
    "recent": []
  },
  "tmdb_api_key_configured": true
}
```

### 4. POST `/recommend`
Generates recommendation listings for a target movie name.
- **Request**: `POST /recommend`
- **Headers**: `Content-Type: application/json`
- **Payload**:
```json
{
  "movie_name": "Interstellar"
}
```
- **Response Example (200 OK)**:
```json
{
  "searched_movie": {
    "id": 157336,
    "title": "Interstellar",
    "genres": ["Adventure", "Drama", "Science Fiction"],
    "release_year": "2014",
    "rating": 8.1
  },
  "recommendations": [
    {
      "id": 264660,
      "title": "Ex Machina",
      "genres": ["Drama", "Science Fiction"],
      "release_year": "2015",
      "rating": 7.6,
      "popularity": 95.132223
    },
    {
      "id": 272,
      "title": "Batman Begins",
      "genres": ["Action", "Crime", "Drama"],
      "release_year": "2005",
      "rating": 7.5,
      "popularity": 115.02874
    }
  ]
}
```
- **Error Responses**:
  - **400 Bad Request**: Missing or empty query parameter.
  - **404 Not Found**: Movie name not found in the dataset.
  ```json
  {
    "error": "Movie 'NonExistentMovie' not found. Please check spelling or try another movie."
  }
  ```

### 5. GET `/poster/<movie_id>`
Backend proxy endpoint that requests poster data from TMDB using the server-side API Key.
- **Request**: `GET /poster/157336`
- **Response Example (200 OK)**:
```json
{
  "poster_url": "https://image.tmdb.org/t/p/w500/gEU2QvEw1Fg7lsbq5v44R4m2Pjh.jpg"
}
```

---

## Screenshots

### Home Page

<img width="1919" height="746" alt="Screenshot 2026-06-27 222243" src="https://github.com/user-attachments/assets/698f1e7b-bbba-41cd-ab70-3b27f6cc5c0e" />


### Movie Recommendations

<img width="1917" height="843" alt="Screenshot 2026-06-27 222335" src="https://github.com/user-attachments/assets/96094567-d6ee-4410-98ff-2e08dfa1e050" />


### Featured Movies

<img width="1919" height="905" alt="Screenshot 2026-06-27 222406" src="https://github.com/user-attachments/assets/7ac99b3f-8c1c-42b5-aad6-7cd41032dcd0" />

---

##  Future Scope

In future releases, we plan to implement the following advancements to evolve CineMatch into a commercial-grade application:
1. **User Authentication**: Implement registration/login flows using JWT or OAuth (Google, GitHub) so users can save favorites and view recommendation history.
2. **Collaborative Filtering**: Incorporate user rating matrices (e.g. using MovieLens 100k rating data) and apply Matrix Factorization (SVD) or K-Nearest Neighbors (KNN) to recommend movies based on similar users' watch behaviors.
3. **Hybrid Recommendation Engine**: Combine Content-Based (TF-IDF on metadata) and Collaborative Filtering models to balance content relevance and community trends.
4. **Watchlists and Ratings**: Allow users to create custom watchlists, rate movies, and write reviews to feed personal recommendation profiles.
5. **Personalized Dashboards**: Display tailor-made dashboards showing specific recommendations based on user rating history.
6. **Cloud Database Integration**: Migrate from file pickles (`.pkl`) to Postgres/MongoDB for scalability and store trained cosine vectors in a database for fast querying.

---

##  License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Author

**Milan Choudhary**

- Registration No.: INBT019545
- B.Tech CSE (Artificial Intelligence)
- Medi-Caps University
- Internship: iNeuBytes AI Internship

### Project Links
- Live Demo: https://cinematch-ai-tccm.onrender.com
