import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import MovieCard from './movieCard';
import './style.css';

export default function SearchMovie() {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  //const [selectedMovie, setSelectedMovie] = useState(null);
  const [movies, setMovies] = useState([]);
  const [noResults, setNoResults] = useState(false);

  // Fetch movie suggestions as the user types
  useEffect(() => {
    const fetchSuggestions = async () => {
      if (query.length < 2) return setSuggestions([]);
      const url = `https://api.themoviedb.org/3/search/movie?api_key=${process.env.REACT_APP_API_KEY}&language=en-US&query=${query}`;
      const res = await fetch(url);
      const data = await res.json();
      setSuggestions(data.results.filter(movie => movie.poster_path));
    };

    const delay = setTimeout(fetchSuggestions, 300); // debounce
    return () => clearTimeout(delay);
  }, [query]);

  const handleSelect = async (movie) => {
    setQuery(movie.title);
    setFocused(false);
    setSuggestions([]);
    
    try {
      const res = await fetch("http://localhost:5001/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: movie.title, filters: {} })
      });
  
      const data = await res.json();
      const recTitles = data.recommendations;
  
      // Now fetch full movie data from TMDb for each recommendation
      const recommendedMovies = await Promise.all(
        recTitles.map(async (title) => {
          const res = await fetch(`https://api.themoviedb.org/3/search/movie?api_key=${process.env.REACT_APP_API_KEY}&query=${title}`);
          const data = await res.json();
          return data.results?.[0] || null;
        })
      );
  
      //setSelectedMovie(null); // Clear previous selection
      const filtered = recommendedMovies.filter(m => m && m.poster_path);
      setMovies(filtered);
      setNoResults(filtered.length === 0); // 👈 Add this
    } catch (error) {
      console.error("Failed to fetch recommendations:", error);
    }
  };
  const [focused, setFocused] = useState(false);

  const containerRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setFocused(false);
      }
    };
  
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);



  return (
    <div ref={containerRef}>
      <form className="form" onSubmit={(e) => e.preventDefault()}>
        <label className="label" htmlFor="query">Movie Name</label>
        <div className="input-wrapper">
            <input
                ref={inputRef}
                className="input"
                type="text"
                name="query"
                placeholder="Enter movie name..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onFocus={() => setFocused(true)}
            />
            <AnimatePresence>
            {query && (
                <motion.button
                className="clear-btn"
                onClick={() => {
                    setQuery("");
                    inputRef.current.focus(); // Refocus input
                }}
                type="button"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                >
                ✖
                </motion.button>
            )}
            </AnimatePresence>
        </div>
      </form>

      {/* Animated suggestion dropdown */}
      <AnimatePresence>
        {focused && query.length > 1 && suggestions.length > 0 && (
          <motion.ul
            className="suggestion-list"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            {suggestions.map(movie => (
                <motion.li
                    key={movie.id}
                    className="suggestion-item-with-poster"
                    onClick={() => handleSelect(movie)}
                    whileHover={{ scale: 1.02 }}
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    >
                    <img
                        src={`https://image.tmdb.org/t/p/w92${movie.poster_path}`}
                        alt={movie.title}
                        className="suggestion-poster"
                    />
                    <span className="suggestion-title">{movie.title}</span>
                </motion.li>
            ))}
          </motion.ul>
        )}
      </AnimatePresence>
      <AnimatePresence>
        {movies.length > 0 && (
            <motion.div
            className="card-list"
            key={"recommendations"}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ duration: 0.25, ease: "anticipate" }}
            >
            {movies.map((movie) => (
            <MovieCard key={movie.id} movie={movie} />))}
            </motion.div>
        )}
        </AnimatePresence>
        {noResults && (
        <div className="no-results">
            <p>No recommendations found for this movie.</p>
        </div>
        )}
    </div>
  );
}
