// FloatingHelpButton.jsx - Modern, Predictable
import React, { useState, useEffect } from "react";
import "../styles/floatingButton.css";
import VoiceAssistant from "./VoiceAssistant";
import "../styles/voiceAssistant.css";

const FloatingHelpButton = () => {
  const [showAssistant, setShowAssistant] = useState(false);
  const [autoPlayWelcome, setAutoPlayWelcome] = useState(false);
  const [isFirstVisit, setIsFirstVisit] = useState(false);

  // 🌟 Detect first visit
  useEffect(() => {
    const hasVisited = localStorage.getItem("pauz_has_visited_before");
    if (!hasVisited) {
      setIsFirstVisit(true);
      // Optional: auto-show assistant on first visit
      // setShowAssistant(true);
      // setAutoPlayWelcome(true);
      // localStorage.setItem("pauz_has_visited_before", "true");
    }
  }, []);

  // 🌟 Open assistant manually
  const openAssistant = () => {
    setShowAssistant(true);
    setAutoPlayWelcome(true);
  };

  // 🌟 Close assistant
  const handleAssistantClose = () => {
    setShowAssistant(false);
    setAutoPlayWelcome(false);

    if (isFirstVisit) {
      localStorage.setItem("pauz_has_visited_before", "true");
      setIsFirstVisit(false);
    }
  };

  return (
    <>
      {/* Floating Help Button */}
      <button
        className={`floating-help-btn ${isFirstVisit ? "first-visit" : ""}`}
        onClick={openAssistant}
        title="Need help?"
      >
       Need Help?
      </button>

      {/* Voice Assistant */}
      <VoiceAssistant
        isVisible={showAssistant}
        onClose={handleAssistantClose}
        autoPlayWelcome={autoPlayWelcome}
      />
    </>
  );
};

export default FloatingHelpButton;
