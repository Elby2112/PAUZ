import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import "../styles/guidedJournal.css";

import quillIcon from "../assets/icons/quill-pen-2.png";
import micIcon from "../assets/icons/microphone.png";
import diskIcon from "../assets/icons/download.png";
import editIcon from "../assets/icons/selection.png";
import saveIcon from "../assets/icons/save.png";
import CategoryModal from "../components/CategoryModal";

const PLACEHOLDER_PROMPTS = [
  "How do you feel today?",
  "What are you grateful for?",
  "Describe a recent challenge.",
  "What made you happy today?",
  "What did you learn today?",
  "Set one goal for tomorrow."
];

//const API_BASE = "http://localhost:8000";
const API_BASE="http://155.138.238.152:8000"
const getAuthHeaders = () => {
  const token = localStorage.getItem("pauz_token");
  if (!token) return null;
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
};

const GuidedJournaling = () => {
  const { category } = useParams();
  const navigate = useNavigate();
  const [answers, setAnswers] = useState(Array(6).fill(""));
  const [prompts, setPrompts] = useState(PLACEHOLDER_PROMPTS);
  const [loading, setLoading] = useState(false);
  const [showTopicSelector, setShowTopicSelector] = useState(false);
  const [mode, setMode] = useState("write");
  const [recording, setRecording] = useState(false);
  const [saveStatus, setSaveStatus] = useState({ type: "", message: "" });
  const [currentJournalId, setCurrentJournalId] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  const fetchPrompts = async (topic) => {
    const headers = getAuthHeaders();
    if (!headers) {
      setPrompts(PLACEHOLDER_PROMPTS);
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/guided_journal/prompts`, {
        method: "POST",
        headers,
        body: JSON.stringify({ topic }),
      });

      if (!res.ok) {
        throw new Error(`Failed to load prompts: ${res.status}`);
      }

      const data = await res.json();
      const mappedPrompts = data.map((p) => {
        if (typeof p === "string") return p;
        if (p.text) return p.text;
        if (p.question) return p.question;
        return JSON.stringify(p);
      });
      
      setPrompts(mappedPrompts);
      setAnswers(Array(mappedPrompts.length).fill(""));
      setCurrentJournalId(null);

    } catch (err) {
      console.error("Error fetching prompts:", err);
      setPrompts(PLACEHOLDER_PROMPTS);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const headers = getAuthHeaders();
    if (!headers) return;

    const topic = category || "Random Prompt Flow";
    fetchPrompts(topic);
  }, [category]);

  const handleAnswerChange = (index, value) => {
    const updated = [...answers];
    updated[index] = value;
    setAnswers(updated);
  };

  const saveJournal = async () => {
    const headers = getAuthHeaders();
    if (!headers) {
      setSaveStatus({
        type: "error",
        message: "Please log in to save your journal."
      });
      setTimeout(() => setSaveStatus({ type: "", message: "" }), 3000);
      navigate("/login");
      return;
    }

    const hasContent = answers.some(answer => answer.trim().length > 0);
    if (!hasContent) {
      setSaveStatus({
        type: "warning",
        message: "Please write at least one response before saving."
      });
      setTimeout(() => setSaveStatus({ type: "", message: "" }), 3000);
      return;
    }

    setIsSaving(true);
    setSaveStatus({ type: "info", message: "Saving your journal..." });

    try {
      const journalData = {
        topic: category || "Random Prompt Flow",
        prompts: prompts.map((text, index) => ({
          id: index + 1,
          text: text
        })),
        entries: answers
          .map((answer, index) => {
            if (!answer.trim()) return null;
            return {
              prompt_id: index + 1,
              prompt_text: prompts[index],
              response: answer.trim(),
              created_at: new Date().toISOString()
            };
          })
          .filter(entry => entry !== null)
      };

      const response = await fetch(`${API_BASE}/guided_journal/`, {
        method: "POST",
        headers,
        body: JSON.stringify(journalData)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to save journal: ${response.status} - ${errorText}`);
      }

      const journal = await response.json();
      setCurrentJournalId(journal.id);
      
      setSaveStatus({
        type: "success",
        message: "Journal saved successfully!"
      });
      
      setTimeout(() => setSaveStatus({ type: "", message: "" }), 3000);

    } catch (err) {
      console.error("Error saving journal:", err);
      setSaveStatus({
        type: "error",
        message: "Failed to save journal. Please try again."
      });
      setTimeout(() => setSaveStatus({ type: "", message: "" }), 3000);
    } finally {
      setIsSaving(false);
    }
  };


  const exportToPDF = async () => {
    const headers = getAuthHeaders();
    if (!headers) {
      setSaveStatus({
        type: "error",
        message: "Please log in to export your journal."
      });
      setTimeout(() => setSaveStatus({ type: "", message: "" }), 3000);
      navigate("/login");
      return;
    }

    if (!currentJournalId) {
      setSaveStatus({
        type: "warning",
        message: "Please save your journal before exporting."
      });
      setTimeout(() => setSaveStatus({ type: "", message: "" }), 3000);
      return;
    }

    setIsExporting(true);
    setSaveStatus({ type: "info", message: "Generating PDF..." });

    try {
      const response = await fetch(`${API_BASE}/guided_journal/${currentJournalId}/export`, {
        method: "POST",
        headers,
      });

      if (!response.ok) {
        throw new Error(`Failed to export PDF: ${response.status}`);
      }

      const data = await response.json();
      
      const link = document.createElement('a');
      link.href = data.pdf_url;
      link.download = `journal-${new Date().toISOString().split('T')[0]}.pdf`;
      link.target = '_blank';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      setSaveStatus({
        type: "success",
        message: "PDF downloaded successfully!"
      });
      
      setTimeout(() => setSaveStatus({ type: "", message: "" }), 3000);

    } catch (err) {
      console.error("Error exporting to PDF:", err);
      setSaveStatus({
        type: "error",
        message: "Failed to generate PDF. Please try again."
      });
      setTimeout(() => setSaveStatus({ type: "", message: "" }), 3000);
    } finally {
      setIsExporting(false);
    }
  };

  return ( 
    <div className="guided-page">
      {saveStatus.message && (
        <div className={`save-status save-status-${saveStatus.type}`}>
          {saveStatus.message}
        </div>
      )}

      <div className="gj-toolbar-wrapper"> 
        <div className="gj-toolbar">
          <button
            className={`gj-icon-btn ${mode === "write" ? "active" : ""}`}
            onClick={() => setMode("write")}
            title="Write your thoughts"
            disabled={isSaving || isExporting}
          >
            <img src={quillIcon} alt="Write" />
          </button>
{/*
          <button
            className={`gj-icon-btn ${mode === "voice" ? "active" : ""}`}
            onClick={() => { setMode("voice"); setRecording(true); }}
            title="Record your voice"
            disabled={isSaving || isExporting}
          >
            <img src={micIcon} alt="Record" />
          </button>
          */
}
          <button 
            className={`gj-icon-btn save-btn ${isSaving ? "loading" : ""}`}
            onClick={saveJournal}
            title="Save Journal Entry"
            disabled={isSaving || isExporting}
          >
            <img src={saveIcon} alt="Save" />
          </button>

          <button 
            className={`gj-icon-btn ${isExporting ? "loading" : ""}`}
            onClick={exportToPDF}
            title="Export to PDF"
            disabled={isExporting || isSaving || !currentJournalId}
          >
            <img src={diskIcon} alt="Export PDF" />
          </button>

          <button
            className="gj-icon-btn change-topic-btn"
            onClick={() => setShowTopicSelector(true)}
            title="Change Topic"
            disabled={isSaving || isExporting}
          >
            <img src={editIcon} alt="Change Topic" />
            Change Topic
          </button>
        </div>
      </div>

      <div className="guided-journal">
        <div className="guided-date">{new Date().toLocaleDateString()}</div>

        <div className="journal-paper">
          {loading ? (
          <div className="quill-loader">
  <p>Generating meaningful prompts…</p>
</div>


            
          ) : (
            prompts.map((q, i) => (
              <div key={i} className="journal-entry">
                <h3 className="journal-question">{`${i + 1}. ${q}`}</h3>
                <textarea
                  className="journal-textarea"
                  value={answers[i]}
                  onChange={(e) => handleAnswerChange(i, e.target.value)}
                  placeholder="Write your reflection here..."
                  disabled={isSaving || isExporting}
                />
              </div>
            ))
          )}
        </div>
      </div>

      {/* ⭐ NEW CATEGORY MODAL */}
      <CategoryModal
        isOpen={showTopicSelector}
        onClose={() => setShowTopicSelector(false)}
        onSelect={(cat) => {
          setShowTopicSelector(false);
          navigate(`/guided/${cat}`);
        }}
      />
    </div>
  );
};

export default GuidedJournaling;
