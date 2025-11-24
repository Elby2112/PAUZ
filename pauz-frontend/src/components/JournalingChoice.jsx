import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/journalingChoice.css";

import freeImg from "../assets/images/freejournal.png";
import guidedImg from "../assets/images/guidedjournal.png";

const JournalingChoice = () => {
  const [selected, setSelected] = useState(null); // free | guided
  const [category, setCategory] = useState(null); // Category selection
  const [step, setStep] = useState(1); // 1 = initial, 2 = category selection
  const navigate = useNavigate();

  const options = [
    { id: "free", title: "Free Journaling", img: freeImg },
    { id: "guided", title: "Guided Journaling", img: guidedImg },
  ];

  const categories = [
    { id: "personal_growth", title: "Personal Growth" },
    { id: "gratitude", title: "Gratitude" },
    { id: "health", title: "Health & Wellness" },
    { id: "career", title: "Career & Professional" },
    { id: "creativity", title: "Creativity" },
    { id: "relationships", title: "Relationships" },
    { id: "goals", title: "Goals & Aspirations" },
    { id: "adventure", title: "Adventure & Travel" },
    { id: "mindfulness", title: "Mindfulness & Meditation" },
  ];

  const handleSelect = (id) => setSelected(id);

  const handleCategorySelect = (categoryId) => setCategory(categoryId);

  const closeModal = () => {
    setSelected(null);
    setCategory(null); // Reset category when modal closes
    setStep(1); // Reset step to initial
  };

  const handleStart = () => {
    if (selected === "free") {
      navigate("/journal");
    } else if (selected === "guided") {
      setStep(2); // Move to category selection step
    }
  };

  const handleCategoryConfirm = () => {
  // Navigate to the guided journal with the selected category
  navigate(`/guided/${category}`);
};


  return (
    <section className="journaling-section">
      <h2 className="journaling-title">
        What kind of journaling are you looking for?
      </h2>

      <div className="journaling-options">
        {options.map((option) => (
          <div
            key={option.id}
            className={`journaling-option ${
              selected === option.id ? "selected" : ""
            }`}
            onClick={() => handleSelect(option.id)}
          >
            <div className="option-left">
              <img src={option.img} alt={option.title} className="option-img" />
              <h3 className="option-title">{option.title}</h3>
            </div>
            <div className="option-arrow">{">"}</div>
          </div>
        ))}
      </div>

      {selected && (
        <div className="modal-overlay" onClick={closeModal}>
          <div
            className={`journaling-modal ${
              selected === "guided" ? "guided-modal" : ""
            }`}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-close" onClick={closeModal}>
              ×
            </div>
            <div className="modal-logo-wrapper">
              <img
                src={selected === "free" ? freeImg : guidedImg}
                alt={
                  selected === "free" ? "Free Journaling" : "Guided Journaling"
                }
                className="modal-logo"
              />
            </div>

            <h3 className="modal-title">
              {selected === "free" ? "Free Journaling" : "Guided Journaling"}
            </h3>

            {selected === "free" ? (
              <>
                <p className="modal-subtitle">
                  Write your thoughts freely without any prompts. Explore your
                  creativity and reflect on your day.
                </p>
                <ul className="modal-list">
                  <li>
                    <span className="feature-icon">🖋️</span> Express yourself freely
                  </li>
                  <li>
                    <span className="feature-icon">🗒️</span> No structure needed
                  </li>
                  <li>
                    <span className="feature-icon">💬</span> Perfect for daily thoughts
                  </li>
                  <li>
                    <span className="feature-icon">✨</span> Unlock your creativity
                  </li>
                </ul>
                <button
                  className="start-now-btn"
                  onClick={() => navigate("/journal")}
                >
                  Start Writing
                </button>
              </>
            ) : selected === "guided" && step === 1 ? (
              <>
                <p className="modal-subtitle">
                  Receive curated prompts to guide your journaling process. Perfect for structured self-reflection.
                </p>

                <ul className="modal-list">
                  <li>
                    <span className="feature-icon">📝</span> Structured prompts
                  </li>
                  <li>
                    <span className="feature-icon">🗒️</span> Step-by-step guidance
                  </li>
                  <li>
                    <span className="feature-icon">🌟</span> Explore deep self-reflection
                  </li>
                  <li>
                    <span className="feature-icon">🎯</span> Track your personal growth
                  </li>
                </ul>

                <button className="start-now-btn" onClick={handleStart}>
                  Start Now
                </button>
              </>
            ) : null}

            {step === 2 && selected === "guided" && (
              <>
                <p className="modal-subtitle">Choose a category to proceed.</p>

                <div className="category-selection">
                  {categories.map((cat) => (
                    <button
                      key={cat.id}
                      className={`category-btn ${
                        category === cat.id ? "selected" : ""
                      }`}
                      onClick={() => handleCategorySelect(cat.id)}
                    >
                      {cat.title}
                    </button>
                  ))}
                </div>

                {category && (
                  <div className="category-confirmation">
                    <p>
                      You selected:{" "}
                      {categories.find((cat) => cat.id === category).title}
                    </p>
                    <button className="start-now-btn" onClick={handleCategoryConfirm}>
                      Confirm and Start
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}
    </section>
  );
};

export default JournalingChoice;
