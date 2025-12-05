import React, { useState, useEffect, useRef } from 'react';
import '../styles/voiceAssistant.css';
import './voiceAssistant_styles.css';

// Icons (you can replace with your actual icons)
const volumeIcon = "🔊";
const muteIcon = "🔇";
const micIcon = "🎤";
const closeIcon = "❌";

const API_BASE = "http://localhost:8000";

const VoiceAssistant = ({ 
  isVisible, 
  onClose, 
  autoPlayWelcome = false,
  showOnMount = false 
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentText, setCurrentText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [userInput, setUserInput] = useState("");
  const [conversation, setConversation] = useState([]);
  const [isListening, setIsListening] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [userContext, setUserContext] = useState(null);
  const [voiceMode, setVoiceMode] = useState(false); // New: for voice-to-voice mode
  
  const audioRef = useRef(null);
  const conversationEndRef = useRef(null);
  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);
  const audioPlayer = useRef(null);

  // Get authentication headers
  const getAuthHeaders = () => {
    const token = localStorage.getItem("pauz_token");
    return {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    };
  };

  // Auto-scroll conversation
  useEffect(() => {
    conversationEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [conversation]);

  // Load user context on mount
  useEffect(() => {
    if (showOnMount) {
      loadUserContext();
    }
  }, [showOnMount]);

  // Auto-play welcome message
  useEffect(() => {
    if (autoPlayWelcome && userContext && isVisible) {
      playWelcomeMessage();
    }
  }, [autoPlayWelcome, userContext, isVisible]);

  // Initialize microphone for voice mode
  useEffect(() => {
    if (voiceMode && isVisible) {
      initializeVoiceMode();
    }
    
    return () => {
      // Cleanup microphone
      if (mediaRecorder.current && mediaRecorder.current.state !== 'inactive') {
        mediaRecorder.current.stop();
      }
    };
  }, [voiceMode, isVisible]);

  const loadUserContext = async () => {
    try {
      const response = await fetch(`${API_BASE}/voice-assistant/user-context`, {
        headers: getAuthHeaders(),
      });
      
      if (response.ok) {
        const context = await response.json();
        setUserContext(context);
      }
    } catch (error) {
      console.error('Failed to load user context:', error);
    }
  };

  const playWelcomeMessage = async () => {
    setIsLoading(true);
    try {
      // Use the new simple welcome endpoint
      const response = await fetch(`${API_BASE}/voice-assistant/welcome-simple`, {
        method: "GET",
        headers: getAuthHeaders(),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          await playAudio(result.audio_data, result.content_type, result.text);
          addToConversation("assistant", result.text);
        }
      }
    } catch (error) {
      console.error('Welcome message failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Voice-to-voice mode functions
  const initializeVoiceMode = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      mediaRecorder.current = recorder;

      recorder.ondataavailable = (e) => audioChunks.current.push(e.data);
      recorder.onstop = async () => {
        await processVoiceQuery();
      };

      // Play welcome message first
      await playWelcomeMessage();
      
      // Then start listening
      setTimeout(() => {
        startVoiceListening();
      }, 1000);

    } catch (err) {
      console.error("Failed to initialize voice mode:", err);
      setVoiceMode(false);
    }
  };

  const startVoiceListening = () => {
    if (!mediaRecorder.current) return;
    
    audioChunks.current = [];
    setIsListening(true);
    mediaRecorder.current.start();
    
    // Auto-stop after 10 seconds
    setTimeout(() => {
      if (mediaRecorder.current.state === "recording") {
        mediaRecorder.current.stop();
      }
    }, 10000);
  };

  const stopVoiceListening = () => {
    if (mediaRecorder.current && mediaRecorder.current.state === "recording") {
      mediaRecorder.current.stop();
    }
  };

  const processVoiceQuery = async () => {
    setIsLoading(true);
    setIsListening(false);
    
    if (audioChunks.current.length === 0) {
      setIsLoading(false);
      setTimeout(() => startVoiceListening(), 1000);
      return;
    }

    try {
      const blob = new Blob(audioChunks.current, { type: "audio/webm" });
      const formData = new FormData();
      formData.append("audio", blob, "recording.webm");

      const response = await fetch(`${API_BASE}/voice-assistant/voice-query`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();

      if (result.success && result.audio_data) {
        // Add both user transcription and assistant response to conversation
        addToConversation("user", result.user_transcription);
        await playAudio(result.audio_data, result.content_type, result.assistant_response);
        addToConversation("assistant", result.assistant_response);
        
        // Restart listening after response
        setTimeout(() => {
          startVoiceListening();
        }, 1000);
      } else {
        throw new Error(result.detail || "Failed to process voice query");
      }

    } catch (error) {
      console.error("Voice query error:", error);
      addToConversation("assistant", "I'm having trouble understanding. Could you try again?");
      
      // Try to recover
      setTimeout(() => {
        startVoiceListening();
      }, 2000);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleVoiceMode = () => {
    setVoiceMode(!voiceMode);
    if (!voiceMode) {
      // Starting voice mode
      setUserInput(""); // Clear any text input
    }
  };

  const playAudio = (audioData, contentType, text) => {
    return new Promise((resolve, reject) => {
      if (isMuted) {
        setCurrentText(text);
        setIsPlaying(false);
        resolve();
        return;
      }

      const audio = new Audio(`data:${contentType};base64,${audioData}`);
      
      audio.onended = () => {
        setIsPlaying(false);
        resolve();
      };
      
      audio.onerror = (error) => {
        setIsPlaying(false);
        reject(error);
      };

      setCurrentText(text);
      setIsPlaying(true);
      audio.play().catch(reject);
    });
  };

  const addToConversation = (speaker, text) => {
    setConversation(prev => [
      ...prev,
      { speaker, text, timestamp: new Date() }
    ]);
  };

  const handleUserInput = async (inputText = userInput) => {
    if (!inputText.trim()) return;

    const userMessage = inputText.trim();
    setUserInput("");
    addToConversation("user", userMessage);

    setIsLoading(true);
    
    try {
      const response = await fetch(`${API_BASE}/voice-assistant/guidance`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({
          question: userMessage,
          context: "journaling_help"
        }),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          await playAudio(result.audio_data, result.content_type, result.text);
          addToConversation("assistant", result.text);
        }
      }
    } catch (error) {
      console.error('Guidance request failed:', error);
      addToConversation("assistant", "I'm having trouble responding right now. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const startListening = () => {
    // If in voice mode, use voice-to-voice
    if (voiceMode) {
      startVoiceListening();
      return;
    }

    // Otherwise use browser speech recognition
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert("Speech recognition is not supported in your browser. Please type your message instead.");
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setUserInput(transcript);
      setIsListening(false);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
      alert("Speech recognition failed. Please try typing your message.");
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.start();
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleUserInput();
    }
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
    if (audioRef.current) {
      audioRef.current.muted = !isMuted;
    }
  };

  if (!isVisible) return null;

  return (
    <div className="voice-assistant-overlay">
      <div className="voice-assistant-container">
        {/* Header */}
        <div className="voice-assistant-header">
          <div className="voice-assistant-title">
            <span className="voice-assistant-icon">🎵</span>
            <h3>PAUZ Voice Assistant</h3>
            {voiceMode && (
              <span className="voice-mode-badge">🎤 Voice Mode</span>
            )}
          </div>
          <div className="voice-assistant-controls">
            <button 
              className={`voice-control-btn ${voiceMode ? 'active' : ''}`}
              onClick={toggleVoiceMode}
              title={voiceMode ? "Switch to Text Mode" : "Switch to Voice Mode"}
            >
              🎤
            </button>
            <button 
              className="voice-control-btn"
              onClick={toggleMute}
              title={isMuted ? "Unmute" : "Mute"}
            >
              {isMuted ? muteIcon : volumeIcon}
            </button>
            <button 
              className="voice-control-btn"
              onClick={() => {
                if (voiceMode) {
                  stopVoiceListening();
                }
                onClose();
              }}
              title="Close Assistant"
            >
              {closeIcon}
            </button>
          </div>
        </div>

        {/* Current Audio Text */}
        {(isPlaying || currentText) && (
          <div className="voice-current-text">
            <div className={`voice-indicator ${isPlaying ? 'speaking' : ''}`}>
              🔊
            </div>
            <p>{currentText}</p>
          </div>
        )}

        {/* Voice Mode Indicator */}
        {voiceMode && (
          <div className="voice-mode-status">
            {isListening && (
              <div className="listening-indicator-full">
                <div className="wave listening"></div>
                <p>Listening... Speak clearly</p>
                <button 
                  className="stop-listening-btn"
                  onClick={stopVoiceListening}
                >
                  ⏹️ Stop
                </button>
              </div>
            )}
            {isLoading && !isListening && (
              <div className="thinking-indicator-full">
                <div className="dots-thinking">
                  <span></span><span></span><span></span>
                </div>
                <p>Thinking...</p>
              </div>
            )}
          </div>
        )}

        {/* Conversation */}
        <div className="voice-conversation">
          {conversation.map((msg, index) => (
            <div 
              key={index} 
              className={`conversation-message ${msg.speaker}`}
            >
              <div className="message-avatar">
                {msg.speaker === "assistant" ? "🎵" : "👤"}
              </div>
              <div className="message-content">
                <p>{msg.text}</p>
                <span className="message-time">
                  {msg.timestamp.toLocaleTimeString()}
                </span>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="conversation-message assistant">
              <div className="message-avatar">🎵</div>
              <div className="message-content loading">
                <div className="voice-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <p>Thinking...</p>
              </div>
            </div>
          )}
          
          <div ref={conversationEndRef} />
        </div>

        {/* Input Controls */}
        {!voiceMode && (
          <div className="voice-input-controls">
            <div className="input-group">
              <button
                className={`voice-mic-btn ${isListening ? 'listening' : ''}`}
                onClick={startListening}
                disabled={isLoading}
                title="Click to speak"
              >
                {micIcon}
                {isListening && <span className="listening-indicator"></span>}
              </button>
              
              <input
                type="text"
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything about journaling..."
                disabled={isLoading}
                className="voice-input"
              />
              
              <button
                className="voice-send-btn"
                onClick={() => handleUserInput()}
                disabled={isLoading || !userInput.trim()}
              >
                Send
              </button>
            </div>
            
            {/* Quick Actions */}
            <div className="quick-actions">
              <button 
                onClick={() => handleUserInput("What can I do here?")}
                disabled={isLoading}
              >
                What can I do?
              </button>
              <button 
                onClick={() => handleUserInput("I'm feeling stuck")}
                disabled={isLoading}
              >
                I'm stuck
              </button>
              <button 
                onClick={playWelcomeMessage}
                disabled={isLoading}
              >
                Welcome Message
              </button>
            </div>
          </div>
        )}

        {/* Voice Mode Instructions */}
        {voiceMode && (
          <div className="voice-mode-instructions">
            <p>🎤 Voice Mode Active</p>
            <p>Just speak naturally - I'm listening!</p>
            <p>Click the 🎤 button to switch back to text mode</p>
          </div>
        )}

        {/* Status Bar */}
        {isMuted && (
          <div className="voice-status muted">
            🔇 Voice is muted - text responses only
          </div>
        )}
      </div>
    </div>
  );
};

export default VoiceAssistant;