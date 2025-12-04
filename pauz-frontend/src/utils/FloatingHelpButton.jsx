// FloatingHelpButton.jsx - INTEGRATED WITH VOICE ASSISTANT
import React, { useState, useEffect } from "react";
import "../styles/floatingButton.css"
import VoiceAssistant from "./VoiceAssistant"; // Import the voice assistant component
import "../styles/voiceAssistant.css"; // Import voice assistant styles

const FloatingHelpButton = () => {
  const [showAssistant, setShowAssistant] = useState(false);
  const [autoPlayWelcome, setAutoPlayWelcome] = useState(false);
  const [isFirstVisit, setIsFirstVisit] = useState(false);

  // 🌟 Detect First Visit
  useEffect(() => {
    const hasVisited = localStorage.getItem("pauz_has_visited_before");
    if (!hasVisited) {
      setIsFirstVisit(true);
      // OPTIONAL: auto show assistant first time
      // setShowAssistant(true);
      // setAutoPlayWelcome(true);
      // localStorage.setItem("pauz_has_visited_before", "true");
    }
  }, []);

  // 🌟 Smart Idle Trigger (2 min)
  useEffect(() => {
    let inactivityTimer;

    const resetTimer = () => {
      clearTimeout(inactivityTimer);

      inactivityTimer = setTimeout(() => {
        if (!showAssistant) {
          setShowAssistant(true);
          setAutoPlayWelcome(false);
        }
      }, 120000); // 2 min idle
    };

    const events = ["mousedown", "keypress", "scroll", "touchstart"];
    events.forEach((event) =>
      document.addEventListener(event, resetTimer, true)
    );

    resetTimer(); // Start immediately

    return () => {
      events.forEach((event) =>
        document.removeEventListener(event, resetTimer, true)
      );
      clearTimeout(inactivityTimer);
    };
  }, [showAssistant]);

  // 🌟 Manual open
  const openAssistant = () => {
    console.log("🎤 Voice Assistant opened");
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
        🎤 Need Help?
      </button>

      {/* Mini Voice Assistant Card */}
      <VoiceAssistant
        isVisible={showAssistant}
        onClose={handleAssistantClose}
        autoPlayWelcome={autoPlayWelcome}
      />
    </>
  );
};

export default FloatingHelpButton;