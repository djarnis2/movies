import '../css/DescriptionLink.css'
import ReactDOM from 'react-dom';

function DescriptionLink({ trigger, movie, closePopup }) {
    if (!trigger) return null;

    return ReactDOM.createPortal(
        <div className="popUp" onClick={closePopup}>
            <div className="innerPopup" onClick={(e) => e.stopPropagation()}>
                <button className='close-btn' onClick={closePopup}>Close</button>

                <div className="movie-description">
                    <h3>{movie?.title || ""}</h3>
                    <br />
                    <p>{movie?.description || "No description available."}</p>
                </div>
            </div>
        </div>,
        document.body
    );
}

export default DescriptionLink;