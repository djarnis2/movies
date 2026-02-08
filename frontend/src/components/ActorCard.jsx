import "../css/ActorCard.css";

const IMG = "https://image.tmdb.org/t/p/w200";

function ActorCard({ actor, onSelect }) {
    return (
            <div className="actor-card" onClick={() => onSelect?.(actor)}>
                <img
                    className="actor-card-img"
                    src={
                        actor.profile_path
                            ? `${IMG}${actor.profile_path}`
                            : "/images/No_Photo.png"
                    }
                    alt={actor.name}
                />
                <div className="actor-card-body">
                    <div className="actor-card-name">{actor.name}</div>
                    <div className="actor-card-role">{actor.character_name}</div>

                    {actor.biography ? (
                        <div className="actor-card-bio">
                            {actor.biography}
                        </div>
                    ) : null}
                </div>
            </div>
    
    );
}

export default ActorCard