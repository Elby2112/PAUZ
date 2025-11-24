import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import logo from "../../assets/images/logo.jpeg";
import "../../styles/auth.css";



export default function Signup() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSignup = (e) => {
    e.preventDefault();

    localStorage.setItem("pauz_user", JSON.stringify({ email }));
    navigate("/");
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <img src={logo} alt="Pauz" className="auth-logo-large" />
        <h2 className="auth-title">Create Account</h2>
        <p className="auth-tagline">Your AI journaling assistant</p>

        <form onSubmit={handleSignup} className="auth-form">
          <input
            type="email"
            placeholder="Email"
            className="auth-input"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Password"
            className="auth-input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <button type="submit" className="auth-btn">
            Sign Up
          </button>
        </form>

        <p className="auth-switch">
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  );
}
