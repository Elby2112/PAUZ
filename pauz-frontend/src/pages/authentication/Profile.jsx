import React, { useState, useEffect } from "react";
import profileIcon from "../../assets/icons/profile.png";
import freeJournalIcon from "../../assets/images/freejournal.png";
import guidedJournalIcon from "../../assets/images/guidedjournal.png";
import flowerIcon from "../../assets/images/flower.png";
import { useNavigate } from "react-router-dom";
import "../../styles/profile.css";

const Profile = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    total_journals: 0,
    total_free_journals: 0,
    total_guided_journals: 0,
    total_flowers: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const user = JSON.parse(localStorage.getItem("pauz_user")) ?? {};
  const API_BASE = "http://localhost:8000";

  useEffect(() => {
    fetchUserStats();
  }, []);

  const fetchUserStats = async () => {
    try {
      const token = localStorage.getItem("pauz_token");
      if (!token) {
        throw new Error("No authentication token found. Please login again.");
      }

      const response = await fetch(`${API_BASE}/stats/overview`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.status === 401) {
        localStorage.removeItem("pauz_token");
        localStorage.removeItem("pauz_user");
        throw new Error("Authentication expired. Please login again.");
      }

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();

      setStats({
        total_journals: data.total_journals || 0,
        total_free_journals: data.total_free_journals || 0,
        total_guided_journals: data.total_guided_journals || 0,
        total_flowers: data.total_flowers || 0
      });
    } catch (err) {
      setError(err.message);
      if (err.message.includes("Authentication")) {
        setTimeout(() => navigate("/login"), 2000);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLoginRedirect = () => navigate("/login");
  const handleRetry = () => {
    setError(null);
    setLoading(true);
    fetchUserStats();
  };

  if (loading) {
    return (
      <div className="profile-container">
        <div className="profile-card">
          <div className="loading-stats">
            <div className="loading-spinner"></div>
            <p>Loading your statistics...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="profile-container">
        <div className="profile-card">
          <div className="error-stats">
            <p>❌ {error}</p>
            <div className="error-actions">
              {error.includes("Authentication") ? (
                <button onClick={handleLoginRedirect} className="login-btn">
                  Go to Login
                </button>
              ) : (
                <button onClick={handleRetry} className="retry-btn">
                  Try Again
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <div className="profile-card">

        {/* Header */}
        <div className="profile-header">
          <img
            src={user.picture || profileIcon}
            alt="Profile Avatar"
            className="profile-avatar"
            crossOrigin="anonymous"
            onError={(e) => (e.target.src = profileIcon)}
          />
          <h2 className="profile-name">{user.name || "Unknown User"}</h2>
          <p className="profile-email">{user.email || ""}</p>
        </div>

        {/* Journal Summary */}
        <div className="journal-summary">
          <div className="journal-card">
            <img src={freeJournalIcon} alt="Free Journal" />
            <div className="journal-info">
              <span className="journal-count">{stats.total_free_journals}</span>
              <span className="journal-label">Free Journals</span>
            </div>
          </div>

          <div className="journal-card">
            <img src={guidedJournalIcon} alt="Guided Journal" />
            <div className="journal-info">
              <span className="journal-count">{stats.total_guided_journals}</span>
              <span className="journal-label">Guided Journals</span>
            </div>
          </div>

          <div className="journal-card flower">
            <img src={flowerIcon} alt="Garden Flowers" />
            <div className="journal-info">
              <span className="journal-count">{stats.total_flowers}</span>
              <span className="journal-label">Garden Flowers</span>
            </div>
          </div>

          <div className="journal-card total">
            <img src={profileIcon} alt="Total Journals" />
            <div className="journal-info">
              <span className="journal-count">{stats.total_journals}</span>
              <span className="journal-label">Total Journals</span>
            </div>
          </div>
        </div>

        <div className="profile-actions">
          <button
            className="profile-btn garden-btn"
            onClick={() => navigate("/garden")}
          >
            🌱 Visit My Garden
          </button>
        </div>

        {/* Progress Section — NEW DESIGN */}
        {/*
        {stats.total_journals > 0 && (
          <div className="progress-section">
            <div className="progress-title">Progress</div>
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${Math.min(stats.total_journals * 10, 100)}%` }}
              ></div>
            </div>
            <p className="progress-text">
              {stats.total_journals} journal entries so far 🌼
            </p>
          </div>
        )}
          */}
      </div>
    </div>
  );
};

export default Profile;
