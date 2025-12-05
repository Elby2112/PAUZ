import React, { useState, useEffect } from "react";
import "../styles/floatingButton.css";
import VoiceAssistantVoiceOnly from "./VoiceAssistantVoiceOnly";
import "../styles/voiceAssistant.css";

const FloatingHelpButton = () => {
  const [showAssistant, setShowAssistant] = useState(false);
  const [isFirstVisit, setIsFirstVisit] = useState(false);

  // Detect First Visit
  useEffect(() => {
    const hasVisited = localStorage.getItem("pauz_has_visited_before");
    if (!hasVisited) {
      setIsFirstVisit(true);
    }
  }, []);

  // Smart Idle Trigger (2 min)
  useEffect(() => {
    let inactivityTimer;

    const resetTimer = () => {
      clearTimeout(inactivityTimer);

      inactivityTimer = setTimeout(() => {
        if (!showAssistant) {
          setShowAssistant(true);
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

  // Manual open
  const openAssistant = () => {
    console.log("🎤 Voice Assistant opened");
    setShowAssistant(true);
  };

  // Close assistant
  const handleAssistantClose = () => {
    setShowAssistant(false);

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

      {/* Voice Assistant */}
      <VoiceAssistantVoiceOnly
        isVisible={showAssistant}
        onClose={handleAssistantClose}
      />
    </>
  );
};

export default FloatingHelpButton;