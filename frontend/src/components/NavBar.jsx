import { Link } from "react-router-dom";
import "../css/Navbar.css"

function NavBar() {
    return (
    <nav className="navbar">
        <div className="navbar-brand">
            <Link to="/">Min Film Database</Link>
        </div>
        <div className="navbar-links">
            <Link to="/" className="nav-link">Alle Film</Link>
            <Link to="/notseen" className="nav-link">Usete Film</Link>
        </div>
    </nav>
    )
}export default NavBar