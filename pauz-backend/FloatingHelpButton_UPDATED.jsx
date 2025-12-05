// FloatingHelpButton.jsx - INTEGRATED WITH VOICE ASSISTANT
import React, { useState, useEffect } from "react";
import "../styles/floatingButton.css"
import VoiceAssistant from "./VoiceAssistant"; // Import the voice assistant component
import "./voiceAssistant.css"; // Import voice assistant styles

const FloatingHelpButton = () => {
  const [showAssistant, setShowAssistant] = useState(false);
  const [autoPlayWelcome, setAutoPlayWelcome] = useState(false);
  const [isFirstVisit, setIsFirstVisit] = useState(false);

  // 🎯 STRATEGY 1: Check if first-time visitor
  useEffect(() => {
    const hasVisited = localStorage.getItem('pauz_has_visited_before');
    if (!hasVisited) {
      setIsFirstVisit(true);
      // Optionally auto-show for first-time visitors
      // Uncomment the next lines if you want to auto-show welcome
      /*
      setShowAssistant(true);
      setAutoPlayWelcome(true);
      localStorage.setItem('pauz_has_visited_before', 'true');
      */
    }
  }, []);

  // 🎯 STRATEGY 2: Detect inactive users (smart trigger)
  useEffect(() => {
    let inactivityTimer;
    
    const resetTimer = () => {
      clearTimeout(inactivityTimer);
      localStorage.setItem('pauz_last_activity', Date.now().toString());
      
      // Show help after 2 minutes of inactivity
      inactivityTimer = setTimeout(() => {
        if (!showAssistant) { // Don't interrupt if already open
          setShowAssistant(true);
          setAutoPlayWelcome(false); // Don't auto-play, just show
        }
      }, 120000); // 2 minutes
    };
    
    // Track user activity
    const events = ['mousedown', 'keypress', 'scroll', 'touchstart'];
    events.forEach(event => {
      document.addEventListener(event, resetTimer, true);
    });
    
    // Start timer
    resetTimer();
    
    return () => {
      events.forEach(event => {
        document.removeEventListener(event, resetTimer, true);
      });
      clearTimeout(inactivityTimer);
    };
  }, [showAssistant]);

  const openAssistant = () => {
    console.log("🎵 Voice Assistant triggered!");
    setShowAssistant(true);
    setAutoPlayWelcome(true); // Play welcome when manually opened
  };

  const handleAssistantClose = () => {
    setShowAssistant(false);
    setAutoPlayWelcome(false);
    localStorage.setItem('pauz_assistant_dismissed', Date.now().toString());
    
    // Mark as visited if this was first visit
    if (isFirstVisit) {
      localStorage.setItem('pauz_has_visited_before', 'true');
      setIsFirstVisit(false);
    }
  };

  return (
    <>
      {/* Floating Help Button */}
      <button 
        className={`floating-help-btn ${isFirstVisit ? 'first-visit' : ''}`} 
        onClick={openAssistant}
        title="Get help from voice assistant"
      >
        🎵 Need Help?
      </button>

      {/* Voice Assistant Component */}
      <VoiceAssistant
        isVisible={showAssistant}
        onClose={handleAssistantClose}
        autoPlayWelcome={autoPlayWelcome}
        showOnMount={false} // Set to true if you want to auto-show on component mount
      />
    </>
  );
};

export default FloatingHelpButton;