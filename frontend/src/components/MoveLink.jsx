import '../css/MovieLink.css'
import ReactDOM from 'react-dom';

function MovieLink({ trigger, url_link, closePopup }) {
    if (!trigger) return null

    return ReactDOM.createPortal(
        <div className="popUp" onClick={closePopup}>
            <div className="innerPopup" onClick={(e) =>e.stopPropagation() }>
                <button className='close-btn' onClick={closePopup}>Luk</button>
                <iframe 
                    src={url_link}
                    title="TMDB"
                    width="100%"
                    height="600px"
                    style={{ border: "none" }}
                />
            </div>
        </div>,
        document.body
    );
}

export default MovieLink
