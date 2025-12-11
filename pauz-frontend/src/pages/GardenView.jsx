import React, { useState, useEffect } from "react";
import FlowerCard from "./FlowerCard";
import "../styles/gardenView.css";

//const API_BASE = "http://localhost:8000";
const API_BASE="https://pauz-3.onrender.com";
const getAuthHeaders = () => {
  const token = localStorage.getItem("pauz_token");
  if (!token) {
    console.warn("No auth token found");
    return null;
  }
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
};

const GardenView = () => {
  const [flowers, setFlowers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [needsLogin, setNeedsLogin] = useState(false);

  useEffect(() => {
    fetchGardenEntries();
  }, []);

  const fetchGardenEntries = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const headers = getAuthHeaders();
      if (!headers) {
        setNeedsLogin(true);
        setLoading(false);
        return;
      }
      
      const response = await fetch(`${API_BASE}/garden/`, {
        method: 'GET',
        headers
      });

      if (response.status === 401) {
        setNeedsLogin(true);
        setLoading(false);
        return;
      }

      if (!response.ok) {
        let errorMessage = `Failed to fetch garden entries (${response.status})`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.message || errorData.detail || errorMessage;
        } catch (e) {
          // If we can't parse JSON, use status text
          errorMessage = response.statusText || errorMessage;
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      
      if (!Array.isArray(data)) {
        console.error('Expected array but got:', data);
        setFlowers([]);
        return;
      }

      const transformedFlowers = data.map((entry, index) => ({
        id: entry.id,
        mood: entry.mood,
        date: entry.date,
        note: entry.note,
        flower_type: entry.flower_type
      }));

      setFlowers(transformedFlowers);
    } catch (err) {
      console.error('Error fetching garden entries:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteFlower = async (flowerId) => {
    try {
      const headers = getAuthHeaders();
      if (!headers) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`${API_BASE}/garden/${flowerId}`, {
        method: 'DELETE',
        headers
      });

      if (response.status === 401) {
        setNeedsLogin(true);
        throw new Error('Authentication required');
      }

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete flower');
      }

      // Remove the flower from local state
      setFlowers(prevFlowers => prevFlowers.filter(flower => flower.id !== flowerId));
      
    } catch (err) {
      console.error('Error deleting flower:', err);
      throw err; // Re-throw to let FlowerCard handle the error
    }
  };

  const handleLogin = () => {
    window.location.href = '/auth/login';
  };

  if (loading) {
    return (
      <section className="garden-section">
        <div className="garden-content">
          <div className="garden-header">
            <h2 className="garden-title">Loading Garden...</h2>
          </div>
        </div>
      </section>
    );
  }

  if (needsLogin) {
    return (
      <section className="garden-section">
        <div className="garden-content">
          <div className="garden-header">
            <h2 className="garden-title">Welcome to Your Garden 🌱</h2>
            <p className="garden-sub">
              Please login to view and grow your emotional garden.
            </p>
            <div className="auth-actions">
              <button onClick={handleLogin} className="login-button">
                Login to View Garden
              </button>
            </div>
          </div>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="garden-section">
        <div className="garden-content">
          <div className="garden-header">
            <h2 className="garden-title">Garden Error</h2>
            <p className="garden-sub">{error}</p>
            <div className="error-actions">
              <button onClick={fetchGardenEntries} className="retry-button">
                Try Again
              </button>
            </div>
          </div>
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
            {flowers.length === 0 
              ? "Start journaling and reflecting with AI to grow your garden!"
              : `Each flower is a mood that grew from your journaling. Single tap to view notes, double-tap to delete flowers.`
            }
          </p>
        </header>

        {flowers.length === 0 ? (
          <div className="empty-garden">
            <div className="empty-garden-message">
              <p>Your garden is empty.</p>
              <p>Create a journal entry and use "Reflect with AI" to plant your first flower!</p>
            </div>
          </div>
        ) : (
          <div className="garden-grid">
            {flowers.map((flower, i) => (
              <FlowerCard
                key={flower.id}
                mood={flower.flower_type || flower.mood}
                date={flower.date}
                note={flower.note}
                index={i}
                id={flower.id}
                onDelete={handleDeleteFlower}
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