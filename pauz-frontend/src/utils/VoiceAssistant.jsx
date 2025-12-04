// VoiceAssistantVoiceOnly.jsx
import React, { useState, useRef } from "react";
import "../styles/voiceAssistant.css";
import micIcon from "../assets/icons/microphone.png"; // Microphone icon

const API_BASE = "http://localhost:8000";

const VoiceAssistantVoiceOnly = ({ isVisible, onClose }) => {
  const [mode, setMode] = useState("idle"); // idle | listening | thinking | speaking | error
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const audioChunks = useRef([]);
  const audioPlayer = useRef(null);
  const [micReady, setMicReady] = useState(false);

  const getAuthHeaders = () => {
    const token = localStorage.getItem("pauz_token");
    return { "Authorization": `Bearer ${token}` };
  };

  // 🌟 Request mic permission and initialize recorder
  const initMic = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);

      recorder.ondataavailable = (e) => audioChunks.current.push(e.data);
      recorder.onstop = async () => {
        setMode("thinking");
        await sendAudioToBackend();
      };

      setMediaRecorder(recorder);
      setMicReady(true);
    } catch (err) {
      console.error("Mic initialization failed:", err);
      setMode("error");
    }
  };

  // 🌟 Start recording
  const startListening = () => {
    if (!mediaRecorder) return;
    audioChunks.current = [];
    setMode("listening");
    mediaRecorder.start();

    setTimeout(() => {
      if (mediaRecorder.state === "recording") {
        mediaRecorder.stop();
      }
    }, 10000); // auto-stop 10s
  };

  // 🌟 Stop recording
  const stopListening = () => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
      mediaRecorder.stop();
    }
  };

  // 🌟 Send audio to backend
  const sendAudioToBackend = async () => {
    if (audioChunks.current.length === 0) {
      setMode("idle");
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

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const result = await response.json();
      if (result.success && result.audio_data) {
        setMode("speaking");
        await playAssistantAudio(result.audio_data, result.content_type);
        setMode("idle");
      } else throw new Error(result.detail || "Voice query failed");
    } catch (err) {
      console.error("Voice query error:", err);
      setMode("error");
    }
  };

  const playAssistantAudio = (audioData, type) => {
    return new Promise((resolve, reject) => {
      try {
        const audio = new Audio(`data:${type};base64,${audioData}`);
        audioPlayer.current = audio;
        audio.onended = () => resolve();
        audio.onerror = reject;
        audio.play();
      } catch (err) {
        reject(err);
      }
    });
  };

  // 🌟 Handle close
  const handleClose = () => {
    stopListening();
    onClose();
  };

  if (!isVisible) return null;

  return (
    <div className="voicecard-overlay">
      <div className="voicecard">
        <div className="voicecard-header">
          <span className="assistant-dot"></span>
          <button className="voicecard-close" onClick={handleClose}>
            ✖
          </button>
        </div>

        <div className="voicecard-body">
          {mode === "idle" && (
            <button
              onClick={() => {
                if (!micReady) initMic();
                else startListening();
              }}
              className="start-btn"
              title={micReady ? "Start Recording" : "Enable Microphone"}
            >
              <img src={micIcon} alt="mic" className="mic-icon" />
            </button>
          )}

          {mode === "listening" && <div className="wave listening"></div>}
          {mode === "thinking" && (
            <div className="dots-thinking">
              <span></span><span></span><span></span>
            </div>
          )}
          {mode === "speaking" && <div className="wave speaking"></div>}
          {mode === "error" && <div className="error-text">Something went wrong. Try again.</div>}
        </div>

        <div className="voicecard-status">
          {mode === "idle" && "Ready"}
          {mode === "listening" && "Listening..."}
          {mode === "thinking" && "Thinking..."}
          {mode === "speaking" && "Speaking..."}
          {mode === "error" && "Error"}
        </div>

        {mode === "listening" && (
          <div className="voicecard-controls">
            <button onClick={stopListening} className="stop-btn" title="Stop Recording">
              ⏹️
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default VoiceAssistantVoiceOnly;
