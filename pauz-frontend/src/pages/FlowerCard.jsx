import React, { useState, useRef } from "react";
import "../styles/flowerCard.css";

const moodMap = {
  happy: { name: "Happy", emoji: "🌻", color: "#FFD166", petal: "#FFECB3" },
  calm: { name: "Calm", emoji: "🪷", color: "#06D6A0", petal: "#D0F6E9" },
  sad: { name: "Sad", emoji: "🔔", color: "#6A4C93", petal: "#D6C7E6" },
  excited: { name: "Excited", emoji: "🌺", color: "#EF476F", petal: "#FFD3DF" },
  reflective: { name: "Reflective", emoji: "💐", color: "#B49FCC", petal: "#E9DFF6" },
  anxious: { name: "Anxious", emoji: "🌸", color: "#5E8FA8", petal: "#DCEFF6" },
  grateful: { name: "Grateful", emoji: "🌼", color: "#FCEFB4", petal: "#FFF6D6" },
};

const FlowerCard = ({ 
  mood = "calm", 
  date = "", 
  note = "", 
  index = 0, 
  id = null,
  onDelete = null 
}) => {
  const m = moodMap[mood] || moodMap["calm"];
  const [open, setOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const tapTimeoutRef = useRef(null);
  const tapCountRef = useRef(0);

  const handleTap = (e) => {
    e.preventDefault();
    
    tapCountRef.current += 1;
    
    if (tapCountRef.current === 1) {
      // First tap - show note after short delay
      tapTimeoutRef.current = setTimeout(() => {
        setOpen((s) => !s);
        tapCountRef.current = 0;
      }, 250);
    } else if (tapCountRef.current === 2) {
      // Double tap - trigger delete
      clearTimeout(tapTimeoutRef.current);
      tapCountRef.current = 0;
      handleDelete(e);
    }
  };

  const handleDelete = async (e) => {
    e.stopPropagation();
    
    if (!id || !onDelete || isDeleting) return;
    
    setIsDeleting(true);
    
    if (window.confirm("Remove this flower from your garden?")) {
      try {
        await onDelete(id);
      } catch (error) {
        console.error("Failed to delete flower:", error);
        alert("Failed to delete flower. Please try again.");
      }
    }
    
    setIsDeleting(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      setOpen((s) => !s);
    } else if (e.key === "Delete" || e.key === "Backspace") {
      e.preventDefault();
      handleDelete(e);
    }
  };

  return (
    <div
      className={`flower-card ${isDeleting ? 'deleting' : ''}`}
      style={{ ["--delay"]: `${index * 0.08}s` }}
      onClick={handleTap}
      onDoubleClick={(e) => {
        e.preventDefault();
        handleDelete(e);
      }}
      role="button"
      tabIndex={0}
      onKeyDown={handleKeyDown}
      aria-pressed={open}
      aria-label={`Flower: ${m.name} on ${date}. Double-tap to delete, single tap to view note`}
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
        <div className="flower-date">{date}</div>
      </div>

      <div className="flower-stem" aria-hidden>
        <span className="stem-line" />
        <span className="leaf" />
      </div>

      {open && (
        <div className="flower-note">
          <div className="note-text">{note || "No note saved."}</div>
          <div className="note-hint">Tap again to close • Double-tap to delete</div>
        </div>
      )}
    </div>
  );
};

export default FlowerCard;