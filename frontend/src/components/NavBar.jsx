import { Link, useLocation } from "react-router-dom";
import "../css/Navbar.css"

function NavBar({ onClearSearch = () => {} }) {
    const location = useLocation();

    const handleClick = (path) => (e) => {
        onClearSearch();
        if (location.pathname === path) {
            e.preventDefault();
            window.scrollTo(0, 0);
        }
    };

    return (
    <nav className="navbar">
        <div className="navbar-brand">
            <Link to="/" onClick={handleClick("/")} >
                Min Film Database
            </Link>
        </div>

        <div className="navbar-links">
            <Link to="/" className="nav-link" onClick={handleClick("/")} >
                All Movies
            </Link>
            
            <Link to="/notseen" className="nav-link" onClick={handleClick("/notseen")} >
                Unseen Movies
            </Link>
            <Link to="/imports" className="nav-link" onClick={handleClick("/imports")} >
                Imports
            </Link>
        </div>
    </nav>
    )
}

export default NavBar;