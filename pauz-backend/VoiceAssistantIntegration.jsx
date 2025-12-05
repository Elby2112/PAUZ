// Example of how to integrate VoiceAssistant into your main app

import React, { useState, useEffect } from 'react';
import VoiceAssistant from './VoiceAssistant';

const VoiceAssistantIntegration = () => {
  const [showAssistant, setShowAssistant] = useState(false);
  const [autoPlayWelcome, setAutoPlayWelcome] = useState(false);
  const [showOnMount, setShowOnMount] = useState(false);

  // Strategy 1: Show on first visit
  useEffect(() => {
    const hasVisitedBefore = localStorage.getItem('pauz_has_visited_before');
    
    if (!hasVisitedBefore) {
      // First time visitor - show welcome
      setShowOnMount(true);
      setAutoPlayWelcome(true);
      setShowAssistant(true);
      
      // Mark as visited
      localStorage.setItem('pauz_has_visited_before', 'true');
    }
  }, []);

  // Strategy 2: Show on manual trigger (e.g., button click)
  const handleAssistantClick = () => {
    setShowAssistant(true);
    setAutoPlayWelcome(true); // Auto-play welcome when opened
  };

  // Strategy 3: Show after certain conditions
  const checkForAssistantTrigger = () => {
    // Example: Show if user seems stuck
    const lastActivity = localStorage.getItem('pauz_last_activity');
    const timeSinceLastActivity = Date.now() - parseInt(lastActivity || '0');
    
    // If inactive for 2 minutes, offer help
    if (timeSinceLastActivity > 120000) {
      setShowAssistant(true);
      setAutoPlayWelcome(false); // Don't auto-play, just show
    }
  };

  // Close handler
  const handleCloseAssistant = () => {
    setShowAssistant(false);
    setAutoPlayWelcome(false);
    // Remember when user closed assistant
    localStorage.setItem('pauz_assistant_dismissed', Date.now().toString());
  };

  return (
    <div>
      {/* Your existing app content */}
      <div className="app-content">
        {/* ... your existing components ... */}
        
        {/* Voice Assistant Trigger Button */}
        <button
          className="voice-assistant-trigger"
          onClick={handleAssistantClick}
          title="Get help from voice assistant"
        >
          🎵 Need Help?
        </button>
      </div>

      {/* Voice Assistant Component */}
      <VoiceAssistant
        isVisible={showAssistant}
        onClose={handleCloseAssistant}
        autoPlayWelcome={autoPlayWelcome}
        showOnMount={showOnMount}
      />
    </div>
  );
};

// CSS for the trigger button (add to your main CSS file)
const triggerButtonStyles = `
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
`;

export default VoiceAssistantIntegration;