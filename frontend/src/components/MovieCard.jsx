import "../css/MovieCard.css";
import MovieLink from "./MoveLink";
import { useState } from "react";


function MovieCard({ movie, seenIds, toggle }) {
    const [btnPopup, setBtnPopup] = useState(false);

    const markAsSeen = () => {
        const seen = JSON.parse(localStorage.getItem("seenMovies") || "[]");
        if (!seen.includes(movie.id)) {
            const updated = [...seen, movie.id];
            localStorage.setItem("seenMovies", JSON.stringify(updated));
            
            console.log(seen.length);
            console.log(`Marked ${movie.title} as seen`)
        }
        else {
            const updated = seen.filter((id) => id !== movie.id);
            localStorage.setItem("seenMovies", JSON.stringify(updated));
            console.log(seen.length);
            console.log(`Unmarked ${movie.title} as seen`)
        }
    };


    const IMG = "https://image.tmdb.org/t/p/w500";
    const baseurl = "https://www.themoviedb.org/";
    const movie_url = movie.rel_url;
    const url = baseurl + movie_url;
    return <div className="movie-card">
        <div className="movie-poster">
            <img
                src={movie.poster_path
                    ? `${IMG}${movie.poster_path.replace(/^\/t\/p\//, "/")}`
                    : "/images/no-poster.png"
                }
                alt={movie.title} />
            <div className="movie-overlay">
                <button className="on-viewed-btn" onClick={() => toggle(movie.id)}>
                    {seenIds.includes(movie.id)
                        ? <img src="/images/icons8-eye-48.png" alt="Seen" />
                        : <img src="/images/icons8-unseen-48 (1).png" alt="Unseen" />}
                </button>
            </div>
        </div>
        <div className="movie-info">

            <h3>{movie.title} &nbsp; ⭐ {movie.rating}% &nbsp; <img src="/images/year.png" height="12" /> {movie.year}</h3>
            <div className="movie-description">
                <p>{movie.description}</p>
            </div>
            <button className="TMDB-btn" onClick={() => setBtnPopup(true)}>TMDB</button>

            <MovieLink
                trigger={btnPopup}
                url_link={url}
                closePopup={() => setBtnPopup(false)}>
            </MovieLink>
        </div>

    </div>
}

export default MovieCard