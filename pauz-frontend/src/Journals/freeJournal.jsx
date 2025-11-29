// FreeJournal.jsx
import React, { useState, useEffect } from "react";
import "../styles/freeJournal.css";

import quillIcon from "../assets/icons/quill-pen-2.png";
import micIcon from "../assets/icons/microphone.png";
import diskIcon from "../assets/icons/download.png";
import magicIcon from "../assets/icons/magic.png";
import journalIcon from "../assets/icons/journaling.png";
import saveIcon from "../assets/icons/save.png";
import hintIcon from "../assets/icons/tips.png";

const API_BASE = "http://localhost:8000";

// Enhanced error detection
const detectErrorType = (error) => {
  if (error.message.includes('Failed to fetch') || error.message.includes('CORS')) {
    return 'CORS';
  }
  if (error.message.includes('401')) {
    return 'AUTH';
  }
  if (error.message.includes('Network')) {
    return 'NETWORK';
  }
  return 'UNKNOWN';
};

const getAuthHeaders = () => {
  const token = localStorage.getItem("pauz_token");
  if (!token) {
    return {};
  }
  
  return { 
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}` 
  };
};

const FreeJournal = () => {
  const [mode, setMode] = useState("write");
  const [text, setText] = useState("");
  const [aiOpen, setAiOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [date, setDate] = useState("");
  const [recording, setRecording] = useState(false);

  const [sessionId, setSessionId] = useState(null);
  const [hints, setHints] = useState([]);
  const [hintLoading, setHintLoading] = useState(false);
  const [error, setError] = useState(null);
  const [errorType, setErrorType] = useState(null);

  useEffect(() => {
    const today = new Date();
    setDate(today.toLocaleDateString("en-GB"));
  }, []);

  useEffect(() => {
    if (sessionId) {
      fetchHints();
    }
  }, [sessionId]);

  const createSession = async () => {
    try {
      setError(null);
      setErrorType(null);

      const res = await fetch(`${API_BASE}/freejournal/`, {
        method: "POST",
        headers: getAuthHeaders(),
      });

      if (!res.ok) {
        if (res.status === 401) {
          localStorage.removeItem("pauz_token");
          throw new Error("Authentication failed. Please log in again.");
        }
        
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Failed to create session (status ${res.status})`);
      }

      const data = await res.json();
      const sid = data.session_id ?? data.sessionId ?? data.id ?? null;
      if (sid) setSessionId(sid);
      return data;
    } catch (err) {
      const detectedErrorType = detectErrorType(err);
      setErrorType(detectedErrorType);
      
      if (detectedErrorType === 'CORS') {
        setError("CORS Error: Backend is blocking requests. Please check backend CORS configuration.");
      } else {
        setError(err.message || "Failed to create session");
      }
      
      return null;
    }
  };

  const saveContent = async () => {
    setError(null);
    setErrorType(null);

    let sid = sessionId;
    if (!sid) {
      const created = await createSession();
      sid = created?.session_id ?? created?.sessionId ?? created?.id;
      if (!sid) {
        setError("No session available to save content.");
        return;
      }
      setSessionId(sid);
    }

    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/freejournal/${sid}/save`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ content: text }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Failed to save journal content (status ${res.status})`);
      }

      await res.json();
      setLoading(false);
    } catch (err) {
      const detectedErrorType = detectErrorType(err);
      setErrorType(detectedErrorType);
      setError(err.message || "Failed to save content");
      setLoading(false);
    }
  };

  const requestHint = async () => {
    setHintLoading(true);
    setError(null);
    setErrorType(null);

    try {
      let sid = sessionId;
      if (!sid) {
        const created = await createSession();
        sid = created?.session_id ?? created?.sessionId ?? created?.id;
        setSessionId(sid);
        if (!sid) throw new Error("Could not create session for hint");
      }

      const res = await fetch(`${API_BASE}/freejournal/${sid}/hints`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ current_content: text || "" }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Failed to fetch hint (status ${res.status})`);
      }

      const hintData = await res.json();
      setHints((prev) => [hintData, ...prev]);
      setHintLoading(false);
    } catch (err) {
      const detectedErrorType = detectErrorType(err);
      setErrorType(detectedErrorType);
      
      if (detectedErrorType === 'CORS') {
        setError("CORS Error: Cannot connect to backend. Check if backend is running and CORS is configured.");
      } else {
        setError(err.message || "Failed to get hint");
      }
      
      setHintLoading(false);
    }
  };

  const fetchHints = async () => {
    if (!sessionId) return;
    try {
      const res = await fetch(`${API_BASE}/freejournal/${sessionId}/hints`, {
        method: "GET",
        headers: getAuthHeaders(),
      });
      if (!res.ok) return;
      const data = await res.json();
      setHints(Array.isArray(data) ? data : []);
    } catch (e) {
      console.error("fetchHints error:", e);
    }
  };

  const applyHintToText = (hintText) => {
    const newText = text ? `${text}\n\n${hintText}` : hintText;
    setText(newText);
  };

  const openAIReflection = () => {
    setAiOpen(true);
    setLoading(true);
    setTimeout(() => setLoading(false), 1500);
  };

  const handleLoginRedirect = () => {
    window.location.href = "/login";
  };

  const handleRetryWithNewSession = () => {
    setError(null);
    setErrorType(null);
    setSessionId(null);
    createSession();
  };

  const handleOpenBackend = () => {
    window.open('http://localhost:8000/docs', '_blank');
  };

  return (
    <div className="freejournal-container">
      {/* TOOLBAR */}
      <div className="fj-toolbar-wrapper">
        <div className="fj-toolbar">
          <button
            className={`fj-icon-btn ${mode === "write" ? "active" : ""}`}
            onClick={() => setMode("write")}
            title="Write your thoughts"
          >
            <img src={quillIcon} alt="Write" className={mode === "write" ? "active-icon" : ""} />
          </button>

          <button
            className={`fj-icon-btn ${mode === "voice" ? "active" : ""}`}
            onClick={() => {
              setMode("voice");
              setRecording(true);
            }}
            title="Record your voice"
          >
            <img src={micIcon} alt="Record" className={mode === "voice" ? "active-icon" : ""} />
          </button>

          <button className="fj-icon-btn" title="Get hint" onClick={requestHint} disabled={hintLoading}>
            <img src={hintIcon} alt="Hint" />
          </button>

          <button className="fj-ai-btn" onClick={openAIReflection}>
            <img src={magicIcon} alt="Magic" className="fj-ai-icon" />
            Reflect with AI
          </button>

          <button className="fj-icon-btn" title="Save Entry" onClick={saveContent} disabled={loading}>
            <img src={saveIcon} alt="Save" />
          </button>

          <button className="fj-icon-btn" title="Upload">
            <img src={diskIcon} alt="Upload" />
          </button>
        </div>
      </div>

      {/* JOURNAL PAGE */}
      <main className="fj-journal-page">
        <div className="fj-paper">
          <p className="fj-paper-date">{date}</p>

          {mode === "write" && (
            <textarea
              className="fj-textarea"
              placeholder="Write whatever is on your mind..."
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
          )}
        </div>

        {/* HINT PANEL */}
        <div className="fj-hint-panel">
          {hintLoading && <div className="fj-hint-loading">Looking for ideas…</div>}
          {hints.length === 0 && !hintLoading && (
            <div className="fj-hint-empty">Press the hint icon to get a journaling prompt</div>
          )}

          {hints.map((h, index) => (
            <div key={h.id || index} className="fj-hint-card">
              <div className="fj-hint-text">{h.hint_text || h.text || h.content}</div>
              <div className="fj-hint-actions">
                <button onClick={() => applyHintToText(h.hint_text || h.text || h.content)}>Use</button>
                <button onClick={() => navigator.clipboard.writeText(h.hint_text || h.text || h.content)}>Copy</button>
              </div>
            </div>
          ))}
        </div>
      </main>

      {/* VOICE OVERLAY */}
      {mode === "voice" && recording && (
        <div className="fj-voice-overlay active">
          <div className="fj-voice-box">
            <div className="fj-voice-visual-row">
              <img src={micIcon} alt="Recording" className="fj-voice-icon" />
              <div className="fj-voice-dots-row">
                <span></span><span></span><span></span>
              </div>
              <img src={journalIcon} alt="Journal" className="fj-journal-icon" />
            </div>
            <p className="fj-voice-description">
              Your words will automatically transform into your journal entry.
            </p>
            <button className="fj-voice-finish" onClick={() => setRecording(false)}>
              Finish Recording
            </button>
          </div>
        </div>
      )}

      {/* AI REFLECTION POPUP */}
      {aiOpen && (
        <div className="fj-ai-overlay">
          <div className="fj-ai-box">
            <span className="fj-ai-close-icon" onClick={() => setAiOpen(false)}>
              &times;
            </span>
            {loading ? (
              <div className="fj-ai-loading">
                <div className="fj-ai-spinner"></div>
                <p>✨ Thinking about your thoughts…</p>
              </div>
            ) : (
              <>
                <h2 className="fj-ai-title">AI Reflection Summary</h2>
                <p className="fj-ai-intro">Here's a concise reflection based on your journal entry:</p>
                <div className="fj-ai-content">
                  <div className="fj-ai-section">
                    <h4>🌸 Mood Detected:</h4>
                    <p>Calm and thoughtful</p>
                  </div>
                  <div className="fj-ai-section">
                    <h4>💭 Insight:</h4>
                    <p>You seem to be processing something meaningful in your life.</p>
                  </div>
                  <div className="fj-ai-section">
                    <h4>🌱 Questions to Explore:</h4>
                    <ul>
                      <li>What triggered these thoughts?</li>
                      <li>What do you need right now?</li>
                      <li>How can you take positive steps forward?</li>
                    </ul>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* ENHANCED ERROR DISPLAY */}
      {error && (
        <div className={`fj-error ${errorType === 'CORS' ? 'fj-error-cors' : ''}`}>
          <strong>
            {errorType === 'CORS' ? '🛑 CORS Error' : 
             errorType === 'AUTH' ? '🔐 Auth Error' : 
             '❌ Error'}
          </strong>
          <p>{error}</p>
          <div className="fj-error-actions">
            {errorType === 'CORS' && (
              <>
                <button onClick={handleOpenBackend} className="fj-backend-btn">
                  Check Backend
                </button>
                <button onClick={() => window.location.reload()} className="fj-retry-btn">
                  Reload Page
                </button>
              </>
            )}
            {errorType === 'AUTH' && (
              <button onClick={handleLoginRedirect} className="fj-login-btn">
                Log In Again
              </button>
            )}
            <button onClick={handleRetryWithNewSession} className="fj-retry-btn">
              Retry
            </button>
            <button onClick={() => setError(null)} className="fj-dismiss-btn">
              Dismiss
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default FreeJournal;