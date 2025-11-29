import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import "../styles/guidedJournal.css";

import quillIcon from "../assets/icons/quill-pen-2.png";
import micIcon from "../assets/icons/microphone.png";
import diskIcon from "../assets/icons/download.png";
import editIcon from "../assets/icons/selection.png";

const PLACEHOLDER_PROMPTS = [
  "How do you feel today?",
  "What are you grateful for?",
  "Describe a recent challenge.",
  "What made you happy today?",
  "What did you learn today?",
  "Set one goal for tomorrow."
];

const GuidedJournaling = () => {
  const { category } = useParams();
  const [answers, setAnswers] = useState(Array(6).fill(""));
  const [prompts, setPrompts] = useState(PLACEHOLDER_PROMPTS);
  const [loading, setLoading] = useState(false);
  const [showTopicSelector, setShowTopicSelector] = useState(false);
  const [mode, setMode] = useState("write");
  const [recording, setRecording] = useState(false);

  const fetchPrompts = async (topic) => {
    const token = localStorage.getItem("pauz_token");
    if (!token) {
      console.warn("No token found. Using placeholder prompts for testing.");
      setPrompts(PLACEHOLDER_PROMPTS);
      return;
    }

    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/guided_journal/prompts", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ topic }),
      });

      if (!res.ok) {
        throw new Error(`Failed to load prompts: ${res.status}`);
      }

      const data = await res.json();
      console.log("Raw prompts data:", data); // Debugging line

      // Extract just the text from each prompt object
      const mappedPrompts = data.map((p) => {
        if (typeof p === "string") {
          return p; // If it's already a string, use it as is
        } else if (p.text) {
          return p.text; // Use the text property from the object
        } else if (p.question) {
          return p.question; // Fallback to question property
        } else {
          return JSON.stringify(p); // Last resort: stringify the whole object
        }
      });
      
      setPrompts(mappedPrompts);

    } catch (err) {
      console.error("Error fetching prompts:", err);
      setPrompts(PLACEHOLDER_PROMPTS);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem("pauz_token");
    if (!token) {
      console.warn("No token found. Using placeholder prompts.");
      setPrompts(PLACEHOLDER_PROMPTS);
      return;
    }

    const topic = category || "Random Prompt Flow";
    fetchPrompts(topic);
  }, [category]);

  const handleAnswerChange = (index, value) => {
    const updated = [...answers];
    updated[index] = value;
    setAnswers(updated);
  };

  const openTopicSelector = () => setShowTopicSelector(true);

  const selectTopic = (topic) => {
    setShowTopicSelector(false);
    fetchPrompts(topic);
  };

  return ( 
    <div className="guided-page">
      {/* TOOLBAR */} 
      <div className="gj-toolbar-wrapper"> 
        <div className="gj-toolbar">
          <button
            className={`gj-icon-btn ${mode === "write" ? "active" : ""}`}
            onClick={() => setMode("write")}
            title="Write your thoughts"
          >
            <img src={quillIcon} alt="Write" className={mode === "write" ? "active-icon" : ""} /> 
          </button>

          <button
            className={`gj-icon-btn ${mode === "voice" ? "active" : ""}`}
            onClick={() => { setMode("voice"); setRecording(true); }}
            title="Record your voice"
          >
            <img src={micIcon} alt="Record" className={mode === "voice" ? "active-icon" : ""} />
          </button>

          <button className="gj-icon-btn save-btn" title="Save Entry">
            <img src={diskIcon} alt="Save" />
          </button>

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
          {loading ? (
            <div className="loading-text">Loading prompts...</div>
          ) : (
            prompts.map((q, i) => (
              <div key={i} className="journal-entry">
                <h3 className="journal-question">{`${i + 1}. ${q}`}</h3>
                <textarea
                  className="journal-textarea"
                  value={answers[i]}
                  onChange={(e) => handleAnswerChange(i, e.target.value)}
                  placeholder="Write your reflection here..."
                />
              </div>
            ))
          )}
        </div>
      </div>

      {/* TOPIC SELECTOR MODAL */}
      {showTopicSelector && (
        <div className="guided-modal-overlay" onClick={() => setShowTopicSelector(false)}>
          <div className="guided-modal" onClick={(e) => e.stopPropagation()}>
            <h3>Select a New Topic</h3>
            <div className="topic-list">
              {[
                "❤️ Emotions & Mental Wellbeing",
                "🌤️ Self-Reflection",
                "👤 Self-Esteem & Identity",
                "🎯 Goals & Productivity",
                "💼 Career & Purpose",
                "💸 Money & Decision-Making",
                "💬 Relationships",
                "🌱 Growth Mindset",
                "🎨 Creativity",
                "✨ Random Prompt Flow"
              ].map((t) => (
                <button key={t} className="topic-item" onClick={() => selectTopic(t)}>{t}</button>
              ))}
            </div>
            <button className="guided-close" onClick={() => setShowTopicSelector(false)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default GuidedJournaling;