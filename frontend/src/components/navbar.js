import { clearAuth, getAuth } from "../utils/auth";
import { useNavigate } from "react-router-dom";
import { Link } from "react-router-dom";
import "../styles/navbar.css";

export default function NavBar() {
  const navigate = useNavigate();
  const auth = getAuth();

  function handleLogout() {
    clearAuth();
    navigate("/login");
  }

  return (
    <div>
      <nav>
        <span className="nav-links">
          <Link to="/">Home</Link>
          <Link to="/task">Create Task</Link>
          <Link to="/login">Login</Link>
          <Link to="/register">Register</Link>
          {auth && auth.admin && (
            <Link to="/users">Users</Link>
          )}
        </span>
        {auth && (
          <span className="login-notice">
            Logged in as {auth.username} {auth.admin && " [admin]"}
          </span>
        )}
        <button onClick={() => handleLogout()}>Logout</button>
      </nav>
    </div>
  );
}
