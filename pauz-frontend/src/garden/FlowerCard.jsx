// FlowerCard.jsx
import React, { useState } from "react";
import "../styles/flowerCard.css";

const moodMap = {
  happy: { name: "Happy", emoji: "🌻", color: "#FFD166", petal: "#FFECB3" },
  calm: { name: "Calm", emoji: "🪷", color: "#06D6A0", petal: "#D0F6E9" },
  sad: { name: "Sad", emoji: "🔔", color: "#6A4C93", petal: "#D6C7E6" },
  excited: { name: "Excited", emoji: "🌺", color: "#EF476F", petal: "#FFD3DF" },
  reflective: { name: "Reflective", emoji: "💐", color: "#B49FCC", petal: "#E9DFF6" },
  anxious: { name: "Anxious", emoji: "🌸", color: "#5E8FA8", petal: "#DCEFF6" },
  grateful: { name: "Grateful", emoji: "🌼", color: "#FCEFB4", petal: "#FFF6D6" },
  peaceful: { name: "Peaceful", emoji: "🌷", color: "#FFB7C5", petal: "#FFE0EC" },
  motivated: { name: "Motivated", emoji: "🌹", color: "#E63946", petal: "#FFCAD4" },
  tired: { name: "Tired", emoji: "🌾", color: "#A8DADC", petal: "#E0F4F8" },
};

const FlowerCard = ({ 
  mood = "calm", 
  date = "", 
  note = "", 
  index = 0,
  flower_type,
  onFlowerClick 
}) => {
  const m = moodMap[mood] || moodMap["calm"];
  const [open, setOpen] = useState(false);

  const handleClick = () => {
    setOpen((s) => !s);
    if (onFlowerClick) {
      onFlowerClick({ mood, date, note, flower_type });
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return "";
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString("en-US", { 
        month: "short", 
        day: "numeric", 
        year: "numeric" 
      });
    } catch {
      return dateString;
    }
  };

  return (
    <div
      className="flower-card"
      style={{ ["--delay"]: `${index * 0.08}s` }}
      onClick={handleClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => { if (e.key === "Enter") handleClick(); }}
      aria-pressed={open}
      aria-label={`${m.name} mood flower from ${formatDate(date)}. ${open ? 'Click to close' : 'Click to view details'}`}
    >
      <div
        className="flower-bubble"
        style={{ background: `linear-gradient(180deg, ${m.petal}, ${m.color})` }}
      >
        <div className="flower-emoji" aria-hidden>
          {m.emoji}
        </div>

        <div className="petals" aria-hidden>
          <span style={{ background: m.petal }} />
          <span style={{ background: m.petal }} />
          <span style={{ background: m.petal }} />
          <span style={{ background: m.petal }} />
        </div>
      </div>

      <div className="flower-info">
        <div className="flower-mood">{m.name}</div>
        <div className="flower-date">{formatDate(date)}</div>
      </div>

      <div className="flower-stem" aria-hidden>
        <span className="stem-line" />
        <span className="leaf" />
      </div>

      {open && (
        <div className="flower-note">
          <div className="note-text">
            <strong>{m.name}</strong>
            <p>{note || "No note saved."}</p>
            {flower_type && (
              <small className="flower-type">Flower: {flower_type}</small>
            )}
          </div>
          <div className="note-hint">Tap again to close</div>
        </div>
      )}
    </div>
  );
};

export default FlowerCard;