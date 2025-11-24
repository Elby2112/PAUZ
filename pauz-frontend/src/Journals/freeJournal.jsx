import React, { useState, useEffect } from "react";
import "../styles/freeJournal.css";

import quillIcon from "../assets/icons/quill-pen-2.png";
import micIcon from "../assets/icons/microphone.png";
import diskIcon from "../assets/icons/download.png";
import magicIcon from "../assets/icons/magic.png";
import journalIcon from "../assets/icons/journaling.png";

const FreeJournal = () => {
  const [mode, setMode] = useState("write");
  const [text, setText] = useState("");
  const [aiOpen, setAiOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [date, setDate] = useState("");
  const [recording, setRecording] = useState(false);

  useEffect(() => {
    const today = new Date();
    setDate(today.toLocaleDateString("en-GB"));
  }, []);

  const openAIReflection = () => {
    setAiOpen(true);
    setLoading(true);
    setTimeout(() => setLoading(false), 1500);
  };

  return (
    <div className="freejournal-container">
      {/* ================== TOOLBAR ================== */}
      <div className="fj-toolbar-wrapper">
        <div className="fj-toolbar">
          {/* WRITE */}
          <button
            className={`fj-icon-btn ${mode === "write" ? "active" : ""}`}
            onClick={() => setMode("write")}
            title="Write your thoughts"
          >
            <img
              src={quillIcon}
              alt="Write"
              className={mode === "write" ? "active-icon" : ""}
            />
          </button>

          {/* RECORD */}
          <button
            className={`fj-icon-btn ${mode === "voice" ? "active" : ""}`}
            onClick={() => {
              setMode("voice");
              setRecording(true);
            }}
            title="Record your voice"
          >
            <img
              src={micIcon}
              alt="Record"
              className={mode === "voice" ? "active-icon" : ""}
            />
          </button>

          {/* SAVE */}
          <button className="fj-icon-btn save-btn" title="Save Entry">
            <img src={diskIcon} alt="Save" />
          </button>

          {/* REFLECT WITH AI */}
          <button
            className="fj-ai-btn"
            onClick={openAIReflection}
            disabled={false}
          >
            <img src={magicIcon} alt="Magic" className="fj-ai-icon" />
            Reflect with AI
          </button>
        </div>
      </div>

      {/* ================== JOURNAL PAGE ================== */}
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
      </main>

      {/* ================== VOICE RECORDING OVERLAY ================== */}
      {mode === "voice" && recording && (
        <div className="fj-voice-overlay active">
          <div className="fj-voice-box">
            {/* Horizontal Flow: Mic → Dots → Journal */}
            <div className="fj-voice-visual-row">
              <img src={micIcon} alt="Recording" className="fj-voice-icon" />

              <div className="fj-voice-dots-row">
                <span></span>
                <span></span>
                <span></span>
              </div>

              <img src={journalIcon} alt="Journal" className="fj-journal-icon" />
            </div>

            {/* Description */}
            <p className="fj-voice-description">
              Your words will automatically transform into your journal entry.
            </p>

            {/* Finish Recording Button */}
            <button
              className="fj-voice-finish"
              onClick={() => setRecording(false)}
            >
              Finish Recording
            </button>
          </div>
        </div>
      )}

      {/* ================== AI REFLECTION POPUP ================== */}
      {aiOpen && (
        <div className="fj-ai-overlay">
          <div className="fj-ai-box">
            {/* CLOSE ICON */}
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
                <p className="fj-ai-intro">
                  Here's a concise reflection based on your journal entry:
                </p>
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
    </div>
  );
};

export default FreeJournal;
