import React, { useEffect, useRef, useState } from "react";
import "../styles/jounalingInfo.css";

const cards = [
  {
    title: "Falling asleep",
    subtitle: "Coastal Campground",
    description:
      "Guided exercises and calming sounds to help you fall asleep faster.",
    colorKey: "card-1",
    img: "/mnt/data/Screenshot 2025-11-21 at 8.31.39 PM.png",
  },
  {
    title: "Bedtime essentials",
    subtitle: "Drift off in Denali",
    description:
      "Nighttime meditations and relaxing visuals to slow your mind down.",
    colorKey: "card-2",
    img: "/mnt/data/Screenshot 2025-11-21 at 8.31.39 PM.png",
  },
  {
    title: "Clear your thoughts",
    subtitle: "Mountain Retreat",
    description:
      "Short journaling prompts to settle racing thoughts before bed.",
    colorKey: "card-3",
    img: "/mnt/data/Screenshot 2025-11-21 at 8.31.39 PM.png",
  },
];

const JournalingInfo = () => {
  const containerRef = useRef(null);
  const [index, setIndex] = useState(0);
  const autoTimer = useRef(null);
  const interactionRef = useRef(false);

  // Auto-advance
  useEffect(() => {
    startAuto();
    // keyboard navigation
    const onKey = (e) => {
      if (e.key === "ArrowRight") next();
      if (e.key === "ArrowLeft") prev();
    };
    window.addEventListener("keydown", onKey);
    return () => {
      stopAuto();
      window.removeEventListener("keydown", onKey);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [index]);

  function startAuto() {
    stopAuto();
    autoTimer.current = setInterval(() => {
      if (!interactionRef.current) next();
    }, 4800);
  }
  function stopAuto() {
    if (autoTimer.current) {
      clearInterval(autoTimer.current);
      autoTimer.current = null;
    }
  }

  function goTo(i) {
    const container = containerRef.current;
    if (!container) return;
    const card = container.children[i];
    if (!card) return;
    card.scrollIntoView({ behavior: "smooth", inline: "center" });
    setIndex(i);
  }

  function next() {
    const nextIndex = (index + 1) % cards.length;
    goTo(nextIndex);
  }
  function prev() {
    const prevIndex = (index - 1 + cards.length) % cards.length;
    goTo(prevIndex);
  }

  // Pause auto on user interaction
  function handlePointerDown() {
    interactionRef.current = true;
    stopAuto();
  }
  function handlePointerUp() {
    interactionRef.current = false;
    startAuto();
  }

  // Keep index synced with scroll (for dots)
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    let raf = null;
    const onScroll = () => {
      if (raf) cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        const children = Array.from(container.children);
        const center = container.scrollLeft + container.offsetWidth / 2;
        let closest = 0;
        let minDist = Infinity;
        children.forEach((c, i) => {
          const cCenter = c.offsetLeft + c.offsetWidth / 2;
          const d = Math.abs(center - cCenter);
          if (d < minDist) {
            minDist = d;
            closest = i;
          }
        });
        setIndex(closest);
      });
    };
    container.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      container.removeEventListener("scroll", onScroll);
      if (raf) cancelAnimationFrame(raf);
    };
  }, []);

  return (
    <section className="journaling-info-hero">
      <div className="hero-inner">
        <div
          className="carousel"
          ref={containerRef}
          onPointerDown={handlePointerDown}
          onPointerUp={handlePointerUp}
          onPointerCancel={handlePointerUp}
        >
          {cards.map((c, i) => (
            <article key={i} className={`carousel-card ${c.colorKey}`}>
              <div className="card-media">
                {/* large background illustration */}
                <img className="bg-illustration" src={c.img} alt={c.title} />
                {/* small stacked mini-cards like screenshot */}
                <div className="mini-stack">
                  <img src={c.img} alt="mini" />
                  <img src={c.img} alt="mini" />
                </div>

                {/* decorative moon / star */}
                <div className="decor-moon" aria-hidden="true">
                  <div className="moon" />
                  <div className="star" />
                </div>
              </div>

              <div className="card-content">
                <div className="search-like">
                  <span className="search-icon">🔍</span>
                  <h3>{c.title}</h3>
                </div>
                <h4 className="card-sub">{c.subtitle}</h4>
                <p className="card-desc">{c.description}</p>
              </div>
            </article>
          ))}
        </div>

        {/* Pagination & controls */}
        <div className="carousel-controls">
          <div className="dots">
            {cards.map((_, i) => (
              <button
                key={i}
                aria-label={`Go to slide ${i + 1}`}
                className={`dot ${i === index ? "active" : ""}`}
                onClick={() => goTo(i)}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default JournalingInfo;
