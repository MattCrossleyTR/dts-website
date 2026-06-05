import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/login.css";
import { setAuth, calculatePasswordStrength } from "../utils/auth";

export default function Register() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [passwordStrength, setPasswordStrength] = useState("Weak");
  const [isAdmin, setIsAdmin] = useState(false);
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  let navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    try {
      const userDetails = {
        username: username,
        password: password,
        admin: isAdmin,
      }
      const response = await fetch("http://localhost:8000/users/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(userDetails),
      });

      if (response.ok) {
        const userId = await response.json();
        setAuth({ ...userDetails, id: userId });
        navigate("/");
      } else {
        let error = (await response.json()).detail;
        if (Array.isArray(error)) {
          error = error[0];
        }
        setError(error);
      }
    } catch (error) {
      console.error(error);
      setError("Error: " + error);
    }
  };

  return (
    <div className="login-container">
      <h2>Register</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="username">Username:</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>
        <div>
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value)
              setPasswordStrength(calculatePasswordStrength(e.target.value))
            }}
          />
        </div>
        <span>Password Strength: {passwordStrength}</span>
        <div>
          <label htmlFor="password">Confirm Password:</label>
          <input
            type="password"
            id="confirm_password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
        </div>
        <div>
          <label>
            <input
              type="checkbox"
              checked={isAdmin}
              onChange={(e) => setIsAdmin(e.target.checked)}
            />
            User is admin
          </label>
        </div>
        <button type="submit">Register</button>
        <span className="error-message">{error}</span>
      </form>
    </div>
  );
}
