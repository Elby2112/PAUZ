import React, { useState, useRef, useEffect } from "react";
import "../styles/voiceAssistant.css";
import micIcon from "../assets/icons/microphone.png";
import closeIcon from "../assets/icons/close.png";

//const API_BASE = "http://localhost:8000";
const API_BASE="http://155.138.238.152:8000"

const VoiceAssistantVoiceOnly = ({ isVisible, onClose }) => {
  const [mode, setMode] = useState("idle"); // idle | listening | thinking | speaking | error
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const audioChunks = useRef([]);
  const audioPlayer = useRef(null);
  const [micReady, setMicReady] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const getAuthHeaders = () => {
    const token = localStorage.getItem("pauz_token");
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  useEffect(() => {
    // cleanup on unmount / closing
    return () => {
      cleanupMedia();
      if (audioPlayer.current) {
        audioPlayer.current.pause();
        audioPlayer.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const cleanupMedia = () => {
    try {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
        mediaRecorderRef.current.stop();
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop());
        streamRef.current = null;
      }
      mediaRecorderRef.current = null;
      audioChunks.current = [];
      setMicReady(false);
    } catch (err) {
      console.warn("cleanup error", err);
    }
  };

  const initMic = async () => {
    setErrorMsg("");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const recorder = new MediaRecorder(stream);
      recorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) audioChunks.current.push(e.data);
      };
      recorder.onstop = async () => {
        setMode("thinking");
        await sendAudioToBackend();
      };
      mediaRecorderRef.current = recorder;
      setMicReady(true);
      // If user clicked to start immediately after permission, start listening:
      startListening();
    } catch (err) {
      console.error("Mic initialization failed:", err);
      setMode("error");
      setErrorMsg("Microphone permission denied or unavailable.");
    }
  };

  const startListening = () => {
    setErrorMsg("");
    if (!mediaRecorderRef.current) {
      initMic();
      return;
    }
    audioChunks.current = [];
    try {
      mediaRecorderRef.current.start();
      setMode("listening");
      // auto-stop guard (10s)
      setTimeout(() => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
          mediaRecorderRef.current.stop();
        }
      }, 10000);
    } catch (err) {
      console.error("Start recording failed:", err);
      setMode("error");
      setErrorMsg("Unable to start recording.");
    }
  };

  const stopListening = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop();
      // mode switches to thinking in onstop handler
    }
  };

  const sendAudioToBackend = async () => {
    if (audioChunks.current.length === 0) {
      setMode("idle");
      return;
    }

    setErrorMsg("");
    try {
      const blob = new Blob(audioChunks.current, { type: "audio/webm" });
      const formData = new FormData();
      formData.append("audio", blob, "recording.webm");

      const response = await fetch(`${API_BASE}/voice-assistant/voice-query`, {
        method: "POST",
        headers: { ...getAuthHeaders() }, // do NOT set Content-Type for FormData
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result = await response.json();

      if (result.success && result.audio_data) {
        setMode("speaking");
        await playAssistantAudio(result.audio_data, result.content_type);
        setMode("idle");
        // keep microphone ready for next recording without re-requesting permission
        setMicReady(Boolean(streamRef.current));
        audioChunks.current = [];
      } else {
        throw new Error(result.detail || "Voice query failed");
      }
    } catch (err) {
      console.error("Voice query error:", err);
      setMode("error");
      setErrorMsg("Voice service error. Try again.");
      // keep mic ready so user can try again
      setMicReady(Boolean(streamRef.current));
    } finally {
      // ensure recorder isn't stuck
      try {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
          mediaRecorderRef.current.stop();
        }
      } catch (e) { /* ignore */ }
    }
  };

  const playAssistantAudio = (audioData, type) => {
    return new Promise((resolve, reject) => {
      try {
        const audio = new Audio(`data:${type};base64,${audioData}`);
        audioPlayer.current = audio;
        audio.onended = () => {
          audioPlayer.current = null;
          resolve();
        };
        audio.onerror = (e) => {
          audioPlayer.current = null;
          reject(e);
        };
        audio.play().catch((err) => {
          // autoplay blocked — fallback to idle with error state
          console.warn("Audio autoplay blocked", err);
          audioPlayer.current = null;
          reject(err);
        });
      } catch (err) {
        reject(err);
      }
    });
  };

  const handleClose = () => {
    cleanupMedia();
    if (audioPlayer.current) {
      audioPlayer.current.pause();
      audioPlayer.current = null;
    }
    onClose();
    setMode("idle");
  };

  if (!isVisible) return null;

  return (
    <div className="va-overlay" role="dialog" aria-modal="true" aria-label="Voice Assistant">
      <div className="va-card">
        <header className="va-header">
          <div className="va-title">
            <div className={`va-dot ${mode === "listening" ? "listening" : mode === "thinking" ? "thinking" : mode === "speaking" ? "speaking" : ""}`} />
            <div className="va-name">Voice Assistant</div>
          </div>
          <button className="va-close" onClick={handleClose} aria-label="Close assistant">
            <img src={closeIcon} alt="Close" />
          </button>
        </header>

        <section className="va-body">
          <div className="va-orb-wrap">
            {/* Ripples appear during listening */}
            <div className={`va-ripple va-ripple-1 ${mode === "listening" ? "active" : ""}`} />
            <div className={`va-ripple va-ripple-2 ${mode === "listening" ? "active" : ""}`} />

            {/* Orb */}
            <div className={`va-orb ${mode}`}>
              <img src={micIcon} alt="microphone" className="va-orb-mic" />
            </div>

            {/* Equalizer during speaking */}
            {mode === "speaking" && (
              <div className="va-eq">
                <span style={{'--h': 0.6}}></span>
                <span style={{'--h': 0.9}}></span>
                <span style={{'--h': 0.45}}></span>
                <span style={{'--h': 0.8}}></span>
                <span style={{'--h': 0.55}}></span>
              </div>
            )}

            {/* Thinking dots */}
            {mode === "thinking" && (
              <div className="va-dots-thinking" aria-hidden>
                <span></span><span></span><span></span>
              </div>
            )}
          </div>
        </section>

        <footer className="va-footer">
          <div className="va-actions">
            {mode === "idle" && (
              <button
                className="va-main-btn"
                onClick={() => (micReady ? startListening() : initMic())}
                title={micReady ? "Start listening" : "Enable microphone"}
              >
                <div className="va-btn-inner">
                  <span>{micReady ? "Speak" : "Enable Mic"}</span>
                </div>
              </button>
            )}

            {mode === "listening" && (
              <button className="va-stop-btn" onClick={stopListening} title="Stop">
                ⏹ Stop
              </button>
            )}

            {mode === "error" && (
              <button className="va-retry-btn" onClick={() => { setMode("idle"); setErrorMsg(""); }}>
                Retry
              </button>
            )}
          </div>

          <div className="va-status">
            {mode === "idle" && "Ready"}
            {mode === "listening" && "Listening…"}
            {mode === "thinking" && "Processing…"}
            {mode === "speaking" && "Speaking…"}
            {mode === "error" && (errorMsg || "Something went wrong")}
          </div>
        </footer>
      </div>
    </div>
  );
};

export default VoiceAssistantVoiceOnly;
