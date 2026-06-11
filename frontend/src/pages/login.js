import { useState } from "react";
import { useNavigate } from "react-router";
import "../styles/login.css";
import { setAuth } from "../utils/auth";
import { BACKEND } from "../constants";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  let navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const body = new URLSearchParams();
      body.append('username', username)
      body.append('password', password)
      const response = await fetch(`${BACKEND}/token`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body
      });

      if (response.ok) {
        const token = await response.json();
        setAuth(token);
        navigate("/");
      } else {
        document.querySelector(".error-message").textContent =
          "Invalid username or password";
      }
    } catch (error) {
      document.querySelector(".error-message").textContent = "Error: " + error;
    }
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
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
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <button type="submit">Login</button>
        <span className="error-message"></span>
      </form>
    </div>
  );
}
