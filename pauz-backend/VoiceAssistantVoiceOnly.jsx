import React, { useState, useEffect, useRef } from "react";
import "../styles/voiceAssistant.css";

const API_BASE = "http://localhost:8000";

const VoiceAssistantVoiceOnly = ({ isVisible, onClose }) => {

  const [mode, setMode] = useState("idle"); 
  // idle | welcoming | listening | thinking | speaking | error

  const [mediaRecorder, setMediaRecorder] = useState(null);
  const audioChunks = useRef([]);
  const audioPlayer = useRef(null);
  const welcomePlayed = useRef(false);

  // Get authentication headers
  const getAuthHeaders = () => {
    const token = localStorage.getItem("pauz_token");
    return {
      "Authorization": `Bearer ${token}`,
    };
  };

  // Ask mic permission + play welcome + auto-start listening
  useEffect(() => {
    if (!isVisible) return;

    const initAssistant = async () => {
      try {
        // Initialize microphone
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const recorder = new MediaRecorder(stream);
        setMediaRecorder(recorder);

        recorder.ondataavailable = (e) => audioChunks.current.push(e.data);
        recorder.onstop = async () => {
          setMode("thinking");
          await sendAudioToBackend();
        };

        // Play welcome message if not played yet
        if (!welcomePlayed.current) {
          await playWelcomeMessage();
          welcomePlayed.current = true;
        }

        // Start listening for user input
        setTimeout(() => {
          startListening(recorder);
        }, 1000); // Small delay after welcome

      } catch (err) {
        console.error("Failed to initialize assistant:", err);
        setMode("error");
      }
    };

    initAssistant();
  }, [isVisible]);

  const playWelcomeMessage = async () => {
    try {
      setMode("welcoming");
      
      const response = await fetch(`${API_BASE}/voice-assistant/welcome-simple`, {
        method: "GET",
        headers: getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();

      if (result.success && result.audio_data) {
        await playAssistantAudio(result.audio_data, result.content_type);
      } else {
        throw new Error(result.detail || "Failed to generate welcome message");
      }

    } catch (error) {
      console.error("Welcome message error:", error);
      // Continue to listening even if welcome fails
      setMode("idle");
    }
  };

  const startListening = (recorder) => {
    if (!recorder) return;
    
    audioChunks.current = [];
    setMode("listening");
    recorder.start();
    
    // Auto-stop after 10 seconds to prevent infinite recording
    setTimeout(() => {
      if (recorder.state === "recording") {
        recorder.stop();
      }
    }, 10000);
  };

  const stopListening = () => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
      mediaRecorder.stop();
    }
  };

  const sendAudioToBackend = async () => {
    if (audioChunks.current.length === 0) {
      setMode("idle");
      setTimeout(() => startListening(mediaRecorder), 1000);
      return;
    }

    try {
      const blob = new Blob(audioChunks.current, { type: "audio/webm" });
      const formData = new FormData();
      formData.append("audio", blob, "recording.webm");

      const response = await fetch(`${API_BASE}/voice-assistant/voice-query`, {
        method: "POST",
        headers: getAuthHeaders(), // ✅ ADD THIS
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();

      if (result.success && result.audio_data) {
        setMode("speaking");
        await playAssistantAudio(result.audio_data, result.content_type);
        
        // ✅ RESTART LISTENING AFTER SPEAKING
        setTimeout(() => {
          startListening(mediaRecorder);
        }, 1000);
      } else {
        throw new Error(result.detail || "Failed to process voice query");
      }

    } catch (error) {
      console.error("Voice query error:", error);
      setMode("error");
      
      // ✅ TRY TO RECOVER AFTER ERROR
      setTimeout(() => {
        setMode("idle");
        startListening(mediaRecorder);
      }, 2000);
    }
  };

  const playAssistantAudio = (audioData, type) => {
    return new Promise((resolve, reject) => {
      try {
        const audio = new Audio(`data:${type};base64,${audioData}`);
        audioPlayer.current = audio;

        audio.onended = () => {
          setMode("idle");
          resolve();
        };

        audio.onerror = (error) => {
          console.error("Audio playback error:", error);
          setMode("error");
          reject(error);
        };

        audio.play();
      } catch (error) {
        console.error("Audio creation error:", error);
        setMode("error");
        reject(error);
      }
    });
  };

  // Manual stop listening (if user wants to interrupt)
  const handleManualStop = () => {
    stopListening();
    setMode("idle");
  };

  if (!isVisible) return null;

  return (
    <div className="voicecard-overlay">
      <div className="voicecard">

        {/* Top Bar */}
        <div className="voicecard-header">
          <span className="assistant-dot"></span>
          <button className="voicecard-close" onClick={() => { 
            stopListening(); 
            onClose(); 
          }}>
            ✖
          </button>
        </div>

        {/* State UI */}
        <div className="voicecard-body">
          
          {/* Welcoming animation */}
          {mode === "welcoming" && (
            <div className="wave speaking"></div>
          )}

          {/* Speaking bubble */}
          {mode === "speaking" && (
            <div className="wave speaking"></div>
          )}

          {/* Listening bubble */}
          {mode === "listening" && (
            <div className="wave listening"></div>
          )}

          {/* Thinking */}
          {mode === "thinking" && (
            <div className="dots-thinking">
              <span></span><span></span><span></span>
            </div>
          )}

          {/* Error */}
          {mode === "error" && (
            <div className="error-text">
              Connection issue. Retrying...
            </div>
          )}

        </div>

        {/* Status Messages */}
        <div className="voicecard-status">
          {mode === "welcoming" && "Welcome!"}
          {mode === "listening" && "Listening..."}
          {mode === "thinking" && "Thinking..."}
          {mode === "speaking" && "Speaking..."}
          {mode === "idle" && "Say something"}
          {mode === "error" && "Reconnecting..."}
        </div>

        {/* Manual Controls */}
        {mode === "listening" && (
          <div className="voicecard-controls">
            <button 
              className="stop-btn"
              onClick={handleManualStop}
              title="Stop listening"
            >
              ⏹️ Stop
            </button>
          </div>
        )}

      </div>
    </div>
  );
};

export default VoiceAssistantVoiceOnly;