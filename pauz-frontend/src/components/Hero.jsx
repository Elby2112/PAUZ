import React from "react";
import "../styles/hero.css"; // create a separate CSS for cleaner styling

const Hero = () => {
  return (
    <section className="hero-section">
      <div className="hero-content">
        <h1 className="hero-title">Welcome to PauZ</h1>
        <p className="hero-subtitle">
          Where your thoughts find their voice
        </p>
        <div className="hero-underline" />
      </div>
    </section>
  );
};

export default Hero;
