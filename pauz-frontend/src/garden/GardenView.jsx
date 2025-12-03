// GardenView.jsx
import React, { useState, useEffect } from "react";
import FlowerCard from "./FlowerCard";
import "../styles/gardenView.css";

const API_BASE = "http://localhost:8000";

const getAuthHeaders = () => {
  const token = localStorage.getItem("pauz_token");
  if (!token) return {};
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
};

const GardenView = () => {
  const [flowers, setFlowers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchGardenEntries();
  }, []);

  const fetchGardenEntries = async () => {
    setLoading(true);
    setError("");
    
    try {
      const headers = getAuthHeaders();
      const response = await fetch(`${API_BASE}/garden/`, {
        method: "GET",
        headers,
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch garden entries: ${response.status}`);
      }

      const data = await response.json();
      
      // Transform backend data to match frontend format
      const transformedFlowers = data.map((entry, index) => ({
        id: entry.id,
        mood: entry.mood,
        date: new Date(entry.created_at).toISOString().split('T')[0], // Format as YYYY-MM-DD
        note: entry.note || `Mood: ${entry.mood}`,
        flower_type: entry.flower_type,
      }));

      setFlowers(transformedFlowers);
    } catch (err) {
      console.error("Error fetching garden entries:", err);
      setError("Unable to load your garden. Please try again.");
      
      // Fallback to mock data if API fails
      setFlowers([
        { id: 1, mood: "happy", date: "2025-01-12", note: "Wrote about a warm memory" },
        { id: 2, mood: "calm", date: "2025-01-11", note: "Meditation helped" },
        { id: 3, mood: "grateful", date: "2025-01-10", note: "Thankful for today" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <section className="garden-section">
        <div className="garden-sky" aria-hidden />
        <div className="garden-content">
          <header className="garden-header">
            <h2 className="garden-title">My Garden</h2>
            <p className="garden-sub">Growing your memories...</p>
          </header>
          <div className="garden-loading">
            <div className="garden-spinner" />
            <p>Planting your flowers...</p>
          </div>
        </div>
        <div className="garden-particles" aria-hidden>
          <span className="p p1" />
          <span className="p p2" />
          <span className="p p3" />
          <span className="p p4" />
        </div>
      </section>
    );
  }

  if (error && flowers.length === 0) {
    return (
      <section className="garden-section">
        <div className="garden-sky" aria-hidden />
        <div className="garden-content">
          <header className="garden-header">
            <h2 className="garden-title">My Garden</h2>
            <p className="garden-sub">Each flower represents a mood from your journaling journey</p>
          </header>
          <div className="garden-error">
            <div className="garden-error-icon">🌱</div>
            <h3>Garden needs water</h3>
            <p>{error}</p>
            <button onClick={fetchGardenEntries} className="garden-retry-btn">
              Try Again
            </button>
          </div>
        </div>
        <div className="garden-particles" aria-hidden>
          <span className="p p1" />
          <span className="p p2" />
          <span className="p p3" />
          <span className="p p4" />
        </div>
      </section>
    );
  }

  return (
    <section className="garden-section">
      <div className="garden-sky" aria-hidden />
      <div className="garden-content">
        <header className="garden-header">
          <h2 className="garden-title">My Garden</h2>
          <p className="garden-sub">
            Each flower is a mood that grew from your journaling. Click a flower to view the entry.
          </p>
          {error && (
            <div className="garden-warning">
              <span>⚠️ {error}</span>
            </div>
          )}
        </header>

        {flowers.length === 0 ? (
          <div className="garden-empty">
            <div className="garden-empty-icon">🌱</div>
            <h3>Your garden is empty</h3>
            <p>Start journaling to grow your first flower!</p>
            <button 
              onClick={() => window.location.href = "/journal"}
              className="garden-action-btn"
            >
              Start Journaling
            </button>
          </div>
        ) : (
          <div className="garden-grid">
            {flowers.map((flower, i) => (
              <FlowerCard
                key={flower.id}
                mood={flower.mood}
                date={flower.date}
                note={flower.note}
                index={i}
              />
            ))}
          </div>
        )}
      </div>

      <div className="garden-particles" aria-hidden>
        <span className="p p1" />
        <span className="p p2" />
        <span className="p p3" />
        <span className="p p4" />
      </div>
    </section>
  );
};

export default GardenView;