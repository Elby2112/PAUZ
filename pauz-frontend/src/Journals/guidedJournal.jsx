import React, { useState } from "react";
import "../styles/guidedJournal.css";

import quillIcon from "../assets/icons/quill-pen-2.png";
import micIcon from "../assets/icons/microphone.png";
import diskIcon from "../assets/icons/download.png";
import editIcon from "../assets/icons/selection.png";

const GuidedJournaling = ({ topic = "Career & Purpose" }) => {
  const [answers, setAnswers] = useState(["", "", "", "", "", ""]);
  const [showTopicSelector, setShowTopicSelector] = useState(false);
  const [mode, setMode] = useState("write");
  const [recording, setRecording] = useState(false);

  // Static prompts (could be dynamic from a backend later)
  const prompts = [
    "What part of your work energizes you most right now?",
    "What tasks drain you, and why do you think that is?",
    "What’s one skill you secretly want to develop?",
    "If nothing were holding you back, what path would you try?",
    "Who inspires you in your field and why?",
    "What would ‘success’ look like for you in 6 months?"
  ];

  const handleAnswerChange = (index, value) => {
    const updated = [...answers];
    updated[index] = value;
    setAnswers(updated);
  };

  const openTopicSelector = () => {
    setShowTopicSelector(true);
  };

  return (
    <div className="guided-page">
      {/* TOOLBAR */}
      <div className="gj-toolbar-wrapper">
        <div className="gj-toolbar">
          {/* WRITE */}
          <button
            className={`gj-icon-btn ${mode === "write" ? "active" : ""}`}
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
            className={`gj-icon-btn ${mode === "voice" ? "active" : ""}`}
            onClick={() => {
              setMode("voice");
              setRecording(true); // Activate recording
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
          <button className="gj-icon-btn save-btn" title="Save Entry">
            <img src={diskIcon} alt="Save" />
          </button>

          {/* CHANGE TOPIC */}
          <button
            className="gj-icon-btn change-topic-btn"
            onClick={openTopicSelector}
            title="Change Topic"
          >
            <img src={editIcon} alt="Change Topic" className="fj-ai-icon" />
            Change Topic
          </button>
        </div>
      </div>

      {/* MAIN JOURNAL AREA */}
      <div className="guided-journal">
        <div className="guided-date">{new Date().toLocaleDateString()}</div>

        <div className="journal-paper">
          {prompts.map((q, i) => (
            <div key={i} className="journal-entry">
              <h3 className="journal-question">{`${i + 1}. ${q}`}</h3>

              <textarea
                className="journal-textarea"
                value={answers[i]}
                onChange={(e) => handleAnswerChange(i, e.target.value)}
                placeholder="Write your reflection here..."
              />
            </div>
          ))}
        </div>
      </div>

      {/* TOPIC SELECTOR MODAL */}
      {showTopicSelector && (
        <div className="guided-modal-overlay" onClick={() => setShowTopicSelector(false)}>
          <div className="guided-modal" onClick={(e) => e.stopPropagation()}>
            <h3>Select a New Topic</h3>

            <div className="topic-list">
              <button className="topic-item">❤️ Emotions & Mental Wellbeing</button>
              <button className="topic-item">🌤️ Self-Reflection</button>
              <button className="topic-item">👤 Self-Esteem & Identity</button>
              <button className="topic-item">🎯 Goals & Productivity</button>
              <button className="topic-item">💼 Career & Purpose</button>
              <button className="topic-item">💸 Money & Decision-Making</button>
              <button className="topic-item">💬 Relationships</button>
              <button className="topic-item">🌱 Growth Mindset</button>
              <button className="topic-item">🎨 Creativity</button>
              <button className="topic-item">✨ Random Prompt Flow</button>
            </div>

            <button className="guided-close">Close</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default GuidedJournaling;
