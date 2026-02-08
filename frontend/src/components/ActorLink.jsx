import '../css/ActorLink.css'
import ReactDOM from 'react-dom';
import ActorCard from "./ActorCard";


function ActorLink({ trigger, actors = [], closePopup }) {
    if (!trigger) return null


    const sortedActors = [...actors].sort(
        (a, b) => (a.cast_order ?? 999) - (b.cast_order ?? 999)
    );

    return ReactDOM.createPortal(
        <div className="popUpActor" onClick={closePopup}>
            <div className="innerPopupActor" onClick={(e) => e.stopPropagation()}>
                <button className='close-btn' onClick={closePopup}>Close</button>
                <div className="actor-list">
                    {actors.length === 0 ? (
                        <p>Loading actors...</p>
                    ) : (
                        sortedActors.map((actor) => (
                            <ActorCard key={actor.id} actor={actor} />
                        ))
                    )}
                </div>
            </div>
        </div>,
        document.body
    );
}

export default ActorLink
