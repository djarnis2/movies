import { useState, useEffect } from "react";
import {
  getMyMovies,
  searchMovies,
  getSeenIds,
  addSeen,
  removeSeen,
} from "../services/api";
import MovieCard from "../components/MovieCard";
import "../css/NotSeen.css";

function NotSeen() {
  const [allMovies,  setAllMovies] = useState([]);   // alle film der IKKE er set
  const [movieList,  setMovies]    = useState([]);   // filtreret visning
  const [seenIds,    setSeenIds]   = useState([]);   // sete id’er (fra DB)
  const [searchQuery, setSearchQuery] = useState("");
  const [error,      setError]     = useState(null);
  const [loading,    setLoading]   = useState(true);

  /* -------- hent film + seen-listen én gang -------- */
  useEffect(() => {
    Promise.all([getMyMovies(), getSeenIds()])
      .then(([films, seen]) => {
        const unseen = films.filter(f => !seen.includes(f.id));
        setAllMovies(unseen);
        setMovies(unseen);
        setSeenIds(seen);
      })
      .catch(() => setError("Failed to load data…"))
      .finally(() => setLoading(false));
  }, []);

  /* -------- lokal søgning -------- */
  const handleSearch = (e) => {
    e.preventDefault();
    if (loading) return;
    setMovies(searchMovies(allMovies, searchQuery));
  };

  /* -------- toggle set / unset -------- */
  const toggleSeen = (id) => {
    if (seenIds.includes(id)) {
      removeSeen(id).then(() =>
        setSeenIds(seenIds.filter(x => x !== id))
      );
    } else {
      addSeen(id).then(() =>
        setSeenIds([...seenIds, id])
      );
    }
  };

  return (
    <div className="home">
      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          placeholder="Search for movies..."
          className="search-input"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <button type="submit" className="search-button">Search</button>
      </form>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <div className="loading">loading…</div>
      ) : (
        <div className="movies-grid">
          {movieList.map(m => (
            <MovieCard
              key={m.id}
              movie={m}
              seenIds={seenIds}      /*  vigtige props  */
              toggle={toggleSeen}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default NotSeen;
