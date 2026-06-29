// CineMatch Client-side JS

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const searchForm = document.getElementById("search-form");
    const movieSearchInput = document.getElementById("movie-search");
    const autocompleteSuggestions = document.getElementById("autocomplete-suggestions");
    
    const recommendationsSection = document.getElementById("recommendations-section");
    const searchedMovieTitleSpan = document.getElementById("searched-movie-title");
    const recommendationsGrid = document.getElementById("recommendations-grid");
    
    const loadingIndicator = document.getElementById("loading-indicator");
    const errorMessageBox = document.getElementById("error-message-box");
    const errorText = document.getElementById("error-text");
    const closeErrorBtn = document.getElementById("close-error-btn");
    const clearResultsBtn = document.getElementById("clear-results-btn");

    // Grids for Home Feed
    const popularMoviesGrid = document.getElementById("popular-movies-grid");
    const trendingMoviesGrid = document.getElementById("trending-movies-grid");
    const recentMoviesGrid = document.getElementById("recent-movies-grid");

    // Autocomplete Debounce Timer
    let autocompleteTimeout;

    // Load home page feed on startup
    loadFeaturedMovies();

    // Close error box
    if (closeErrorBtn) {
        closeErrorBtn.addEventListener("click", () => {
            errorMessageBox.classList.add("d-none");
        });
    }

    // Clear recommendation results
    if (clearResultsBtn) {
        clearResultsBtn.addEventListener("click", () => {
            recommendationsSection.classList.add("d-none");
            movieSearchInput.value = "";
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // Autocomplete Input Listener
    movieSearchInput.addEventListener("input", () => {
        clearTimeout(autocompleteTimeout);
        const query = movieSearchInput.value.trim();

        if (query.length < 2) {
            hideAutocompleteDropdown();
            return;
        }

        // Debounce requests to prevent server flooding
        autocompleteTimeout = setTimeout(() => {
            fetch(`/autocomplete?q=${encodeURIComponent(query)}`)
                .then(res => res.json())
                .then(suggestions => {
                    renderAutocompleteDropdown(suggestions);
                })
                .catch(err => console.error("Autocomplete fetch error:", err));
        }, 200);
    });

    // Hide autocomplete on click outside
    document.addEventListener("click", (e) => {
        if (!searchForm.contains(e.target)) {
            hideAutocompleteDropdown();
        }
    });

    // Form Submission
    searchForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const movieName = movieSearchInput.value.trim();
        if (movieName) {
            hideAutocompleteDropdown();
            getRecommendations(movieName);
        }
    });

    // --- Core Functions ---

    function getRecommendations(movieName) {
        // Reset UI states
        loadingIndicator.classList.remove("d-none");
        recommendationsSection.classList.add("d-none");
        errorMessageBox.classList.add("d-none");

        fetch("/recommend", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ movie_name: movieName })
        })
        .then(async (res) => {
            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.error || "Failed to fetch recommendations.");
            }
            return data;
        })
        .then((data) => {
            displayRecommendations(data);
        })
        .catch((err) => {
            errorText.textContent = err.message;
            errorMessageBox.classList.remove("d-none");
            // Scroll to error box
            errorMessageBox.scrollIntoView({ behavior: "smooth", block: "center" });
        })
        .finally(() => {
            loadingIndicator.classList.add("d-none");
        });
    }

    function displayRecommendations(data) {
        const searchedMovie = data.searched_movie;
        const recommendations = data.recommendations;

        // Set Title
        searchedMovieTitleSpan.textContent = searchedMovie.title;

        // Clean Grid
        recommendationsGrid.innerHTML = "";

        // Build recommendation cards
        recommendations.forEach(movie => {
            const cardCol = createMovieCard(movie, false); // false = small/normal card
            recommendationsGrid.appendChild(cardCol);
            
            // Async fetch actual TMDB poster if available (proxied through backend)
            fetchMoviePoster(movie.id, cardCol.querySelector(".poster-container"));
        });

        // Show Section and Scroll to it
        recommendationsSection.classList.remove("d-none");
        recommendationsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    function loadFeaturedMovies() {
        fetch("/movies/featured")
            .then(res => res.json())
            .then(data => {
                const featured = data.featured;
                
                // Popular
                populateFeaturedGrid(featured.popular, popularMoviesGrid);
                // Trending
                populateFeaturedGrid(featured.trending, trendingMoviesGrid);
                // Recently Released
                populateFeaturedGrid(featured.recent, recentMoviesGrid);
            })
            .catch(err => {
                console.error("Error loading featured movies:", err);
            });
    }

    function populateFeaturedGrid(moviesList, gridElement) {
        gridElement.innerHTML = "";
        
        if (!moviesList || moviesList.length === 0) {
            gridElement.innerHTML = `<div class="col-12 text-center text-muted py-4">No movies available.</div>`;
            return;
        }

        moviesList.forEach(movie => {
            const cardCol = createMovieCard(movie, true); // true = homepage feed grid
            gridElement.appendChild(cardCol);
            
            // Async fetch poster
            fetchMoviePoster(movie.id, cardCol.querySelector(".poster-container"));
        });
    }

    // Creates the HTML element for a movie card
    function createMovieCard(movie, isMini = false) {
        const col = document.createElement("div");
        // Responsive columns:
        // recommendations: 1 on mobile, 3 on tablet, 5 on desktop
        // mini homepage cards: 1 on mobile, 3 on tablet, 6 on desktop
        col.className = isMini 
            ? "col-6 col-sm-4 col-md-3 col-lg-2" 
            : "col-12 col-sm-6 col-md-4 col-lg-2-5 col-xl-2-5"; 
            
        // Note: Bootstrap doesn't have col-lg-2-5 by default, let's map:
        if (!isMini) {
            col.className = "col-6 col-md-4 col-lg-2-5 custom-grid-item";
        }

        // Format genres
        const genresLimit = 2;
        const genresHTML = movie.genres.slice(0, genresLimit).map(genre => 
            `<span class="genre-tag">${genre}</span>`
        ).join("");

        // Format Rating
        const ratingVal = movie.rating > 0 ? movie.rating.toFixed(1) : "N/A";

        // HTML structure with poster placeholder by default
        col.innerHTML = `
            <div class="movie-card h-100" data-movie-title="${escapeHTML(movie.title)}">
                <div class="poster-container">
                    <div class="poster-placeholder">
                        <i class="fa-solid fa-clapperboard placeholder-icon"></i>
                        <div>
                            <div class="placeholder-title">${escapeHTML(movie.title)}</div>
                            <span class="badge bg-dark-subtle text-muted small">${movie.release_year}</span>
                        </div>
                    </div>
                    <span class="card-rating-badge">
                        <i class="fa-solid fa-star"></i> ${ratingVal}
                    </span>
                </div>
                <div class="card-details">
                    <div class="movie-title text-truncate" title="${escapeHTML(movie.title)}">${escapeHTML(movie.title)}</div>
                    <div class="movie-meta">
                        <span class="me-2"><i class="fa-regular fa-calendar me-1"></i>${movie.release_year}</span>
                    </div>
                    <div class="movie-genres-container">
                        ${genresHTML}
                    </div>
                </div>
            </div>
        `;

        // Make card clickable to recommend similar movies
        col.querySelector(".movie-card").addEventListener("click", () => {
            movieSearchInput.value = movie.title;
            getRecommendations(movie.title);
        });

        return col;
    }

    // Proxy TMDB poster fetcher
    function fetchMoviePoster(movieId, posterContainer) {
    console.log("Fetching poster for:", movieId);

    fetch(`/poster/${movieId}`)
        .then(res => res.json())
        .then(data => {
            console.log("Response:", movieId, data);

            if (!data.poster_url) {
                console.log("No poster URL");
                return;
            }

            const img = document.createElement("img");

            img.onload = () => {
                console.log("Image loaded:", movieId);

                const ratingBadge = posterContainer.querySelector(".card-rating-badge");
                posterContainer.innerHTML = "";
                posterContainer.appendChild(img);

                if (ratingBadge) {
                    posterContainer.appendChild(ratingBadge);
                }
            };

            img.onerror = () => {
                console.log("Image failed:", movieId);
            };

            img.className = "poster-img";
            img.alt = "Poster";

            img.src = data.poster_url;
        })
        .catch(err => console.error(err));
}

    // --- Autocomplete Rendering Helpers ---

    function renderAutocompleteDropdown(suggestions) {
        if (!suggestions || suggestions.length === 0) {
            hideAutocompleteDropdown();
            return;
        }

        autocompleteSuggestions.innerHTML = "";
        
        suggestions.forEach(title => {
            const item = document.createElement("div");
            item.className = "autocomplete-item";
            item.innerHTML = `<i class="fa-solid fa-film"></i><span>${escapeHTML(title)}</span>`;
            
            item.addEventListener("click", () => {
                movieSearchInput.value = title;
                hideAutocompleteDropdown();
                getRecommendations(title);
            });
            
            autocompleteSuggestions.appendChild(item);
        });

        autocompleteSuggestions.classList.remove("d-none");
    }

    function hideAutocompleteDropdown() {
        autocompleteSuggestions.classList.add("d-none");
        autocompleteSuggestions.innerHTML = "";
    }

    // Escape HTML utility to prevent XSS
    function escapeHTML(str) {
        if (!str) return "";
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});

// Inject styling for our custom responsive 5-column grid layout on large screens
const styleSheet = document.createElement("style");
styleSheet.innerText = `
@media (min-width: 992px) {
    .custom-grid-item {
        flex: 0 0 20%;
        max-width: 20%;
    }
}
`;
document.head.appendChild(styleSheet);
