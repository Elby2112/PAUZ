// GardenView.jsx
import React from "react";
import FlowerCard from "./FlowerCard";
import "../styles/gardenView.css";

const GardenView = () => {
  const flowers = [
  { id: 1, mood: "happy", date: "2025-11-12", note: "Wrote about a warm memory" },
  { id: 2, mood: "sad", date: "2025-11-11", note: "Missed a friend" },
  { id: 3, mood: "calm", date: "2025-11-10", note: "Meditation helped" },
  { id: 4, mood: "excited", date: "2025-11-09", note: "Started a new project" },
  { id: 5, mood: "reflective", date: "2025-11-08", note: "Jotted long thoughts" },
  { id: 6, mood: "grateful", date: "2025-11-07", note: "Thanked someone today" },
  { id: 7, mood: "anxious", date: "2025-11-06", note: "Felt nervous about work" },
  { id: 8, mood: "happy", date: "2025-11-05", note: "Received a compliment" },
  { id: 9, mood: "calm", date: "2025-11-04", note: "Quiet morning walk" },
  { id: 10, mood: "reflective", date: "2025-11-03", note: "Thought about life goals" },
];

  return (
    <section className="garden-section">
      <div className="garden-sky" aria-hidden />
      <div className="garden-content">
        <header className="garden-header">
          <h2 className="garden-title">My Garden</h2>
          <p className="garden-sub">
            Each flower is a mood that grew from your journaling. Click a flower to view the entry.
          </p>
        </header>

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
