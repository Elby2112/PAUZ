import React, { useRef, useState } from "react";
import "../styles/jounalingInfo.css";

const cards = [
  {
    title: "Mindful Reflection",
    description: "Take a few minutes to reflect and center your thoughts daily.",
    color: "#6BAED6", // Medium sky blue
  },
  {
    title: "Emotional Clarity",
    description: "Writing down feelings brings understanding and inner peace.",
    color: "#9B72B0", // Rich muted purple
  },
  {
    title: "Creative Flow",
    description: "Unlock your imagination and explore new ideas through journaling.",
    color: "#F7A072", // Warm coral-orange
  },
  {
    title: "Stress Release",
    description: "Expressing emotions on paper helps reduce anxiety naturally.",
    color: "#73C9A1", // Soft teal-green
  },
  {
    title: "Track Your Growth",
    description: "Monitor your moods, goals, and achievements over time.",
    color: "#F2D16B", // Vibrant golden yellow
  },
];




const JournalingInfo = () => {
  const containerRef = useRef(null);
  const [activeIndex, setActiveIndex] = useState(0);

  const handleScroll = () => {
    if (!containerRef.current) return;
    const { scrollLeft, offsetWidth } = containerRef.current;
    const index = Math.round(scrollLeft / (offsetWidth * 0.85)); // approx width per card
    setActiveIndex(index);
  };

  const goTo = (i) => {
    if (!containerRef.current) return;
    const cardWidth = containerRef.current.children[i].offsetWidth;
    containerRef.current.scrollTo({ left: i * (cardWidth + 24), behavior: "smooth" });
    setActiveIndex(i);
  };

  return (
    <section className="journaling-info-page">
      <h2 className="page-title">Learn More About Journaling</h2>

      <div
        className="cards-container"
        ref={containerRef}
        onScroll={handleScroll}
      >
        {cards.map((card, i) => (
          <div
            className="benefit-card"
            key={i}
            style={{ backgroundColor: card.color }}
          >
            <h3>{card.title}</h3>
            <p>{card.description}</p>
          </div>
        ))}
      </div>

      <div className="dots">
        {cards.map((_, i) => (
          <button
            key={i}
            className={`dot ${i === activeIndex ? "active" : ""}`}
            onClick={() => goTo(i)}
          />
        ))}
      </div>
    </section>
  );
};

export default JournalingInfo;
