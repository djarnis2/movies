import "../css/MovieCard.css";
import MovieLink from "./MoveLink";
import ActorLink from "./ActorLink";
import { useEffect, useState } from "react";
import DescriptionLink from "./DescriptionLink";


function MovieCard({ movie, seenIds, toggle }) {
    const [btnPopup, setBtnPopup] = useState(false);
    const [actorBtnPopup, setActorBtnPopup] = useState(false);
    const [actors, setActors] = useState([]);
    const [descriptionBtnPopup, setDescriptionBtnPopup] = useState(false)

    useEffect(() => {
        if (!actorBtnPopup) return;

        const loadActors = async () => {
            try {
                const API_BASE = "http://localhost:8000"
                const res = await fetch(`${API_BASE}/movies/${movie.id}`);
                const data = await res.json();

                const profiles = (data.cast ?? []);
                if (profiles.length === 0) {
                    setActors([]);
                    setActorBtnPopup(false)
                    return; // "skip resten"
                }
                setActors(profiles);
            } catch (err) {
                console.error("Failed to load actor profiles, err");
                setActors([]);
            }
        };

        loadActors();
    }, [actorBtnPopup, movie.id]);


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

            <div className="Buttons">
                <button className="Description-btn" onClick={() => setDescriptionBtnPopup(true)}>Description</button>
                <DescriptionLink
                    trigger={descriptionBtnPopup}
                    movie={movie}
                    closePopup={() => setDescriptionBtnPopup(false)}>
                </DescriptionLink>
                <button className="TMDB-btn" onClick={() => setBtnPopup(true)}>TMDB</button>
                <MovieLink
                    trigger={btnPopup}
                    url_link={url}
                    closePopup={() => setBtnPopup(false)}>
                </MovieLink>

                <button className="Actor-btn" onClick={() => setActorBtnPopup(true)}>Actors</button>
                <ActorLink
                    trigger={actorBtnPopup}
                    actors={actors}
                    closePopup={() => setActorBtnPopup(false)}>
                </ActorLink>

            </div>

        </div>

    </div>
}

export default MovieCard