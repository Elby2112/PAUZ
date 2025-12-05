// QUICK SETUP - Add this to your main App component

import React, { useState, useEffect } from 'react';
import VoiceAssistant from './VoiceAssistant';

const App = () => {
  const [showAssistant, setShowAssistant] = useState(false);
  const [autoPlayWelcome, setAutoPlayWelcome] = useState(false);

  // 🎯 STRATEGY 1: First-time visitor welcome
  useEffect(() => {
    const hasVisited = localStorage.getItem('pauz_has_visited_before');
    if (!hasVisited) {
      // First time visitor - show welcome
      setShowAssistant(true);
      setAutoPlayWelcome(true);
      localStorage.setItem('pauz_has_visited_before', 'true');
    }
  }, []);

  // 🎯 STRATEGY 2: Detect inactive users
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

  const handleAssistantClose = () => {
    setShowAssistant(false);
    setAutoPlayWelcome(false);
    localStorage.setItem('pauz_assistant_dismissed', Date.now().toString());
  };

  return (
    <div className="app">
      {/* Your existing app content */}
      <YourExistingComponents />
      
      {/* 🎵 FLOATING HELP BUTTON */}
      <button
        className="voice-assistant-trigger"
        onClick={() => {
          setShowAssistant(true);
          setAutoPlayWelcome(true);
        }}
        title="Get help from voice assistant"
      >
        🎵 Need Help?
      </button>
      
      {/* VOICE ASSISTANT COMPONENT */}
      <VoiceAssistant
        isVisible={showAssistant}
        onClose={handleAssistantClose}
        autoPlayWelcome={autoPlayWelcome}
      />
    </div>
  );
};

// Add this CSS to your main stylesheet
const voiceAssistantStyles = `
.voice-assistant-trigger {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 50px;
  padding: 12px 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
  z-index: 999;
  font-family: inherit;
}

.voice-assistant-trigger:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.voice-assistant-trigger:active {
  transform: translateY(0);
}

@media (max-width: 640px) {
  .voice-assistant-trigger {
    bottom: 10px;
    right: 10px;
    padding: 10px 16px;
    font-size: 12px;
  }
}

/* Optional: Pulse animation for first-time visitors */
@keyframes assistantPulse {
  0% { box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3); }
  50% { box-shadow: 0 4px 12px rgba(102, 126, 234, 0.6); }
  100% { box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3); }
}

.voice-assistant-trigger.first-visit {
  animation: assistantPulse 2s infinite;
}
`;

export default App;