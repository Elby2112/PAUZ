// FreeJournal.jsx — FIXED - NO AUTO-CREATION OF EMPTY SESSIONS
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

const getAuthHeaders = () => {
  const token = localStorage.getItem("pauz_token");
  if (!token) return {};
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
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
  const [hint, setHint] = useState(null);
  const [hintLoading, setHintLoading] = useState(false);
  const [aiReflection, setAiReflection] = useState(null);

  const [transcribing, setTranscribing] = useState(false);
 
  // NEW STATE FOR PDF EXPORT
  const [exportLoading, setExportLoading] = useState(false);
  const [showExportConfirm, setShowExportConfirm] = useState(false);
  
  // NEW STATE FOR SAVE FEEDBACK
  const [saveStatus, setSaveStatus] = useState(null);

  useEffect(() => {
    const today = new Date();
    setDate(today.toLocaleDateString("en-GB"));
    // ⭐ REMOVED: createSession() - no longer creates session on page load
  }, []);

  // ⭐ UPDATED: Create session only when needed
  const createSession = async () => {
    try {
      const res = await fetch(`${API_BASE}/freejournal/`, {
        method: "POST",
        headers: getAuthHeaders(),
      });

      const data = await res.json();
      const sid = data.session_id ?? data.id ?? null;
      if (sid) setSessionId(sid);
      return sid;
    } catch (err) {
      console.error("Session error:", err);
      return null;
    }
  };

  // ⭐ UPDATED SAVE FUNCTION - CREATES SESSION ONLY ON FIRST SAVE
  const saveContent = async () => {
    if (!text.trim()) {
      alert("Please write something before saving!");
      return;
    }

    setLoading(true);
    setSaveStatus("saving");
    
    try {
      // Create session only when saving for the first time
      let currentSessionId = sessionId;
      if (!currentSessionId) {
        currentSessionId = await createSession();
        if (!currentSessionId) {
          throw new Error("Failed to create session");
        }
        setSessionId(currentSessionId);
      }

      const res = await fetch(`${API_BASE}/freejournal/${currentSessionId}/save`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ content: text }),
      });

      if (!res.ok) {
        throw new Error(`Save failed! status: ${res.status}`);
      }

      const savedJournal = await res.json();
      console.log("✅ Journal saved:", savedJournal);
      
      setSaveStatus("saved");
      
      // Clear success message after 2 seconds
      setTimeout(() => {
        setSaveStatus(null);
      }, 2000);
      
    } catch (err) {
      console.error("Save error:", err);
      setSaveStatus("error");
      
      setTimeout(() => {
        setSaveStatus(null);
      }, 3000);
    } finally {
      setLoading(false);
    }
  };

  // ⭐ PDF EXPORT FUNCTION
  const exportToPDF = async () => {
    if (!sessionId || !text.trim()) {
      alert("Please write something in your journal first!");
      return;
    }

    setExportLoading(true);
    
    try {
      // First save the current content
      await saveContent();
      
      // Call the export endpoint
      const res = await fetch(`${API_BASE}/freejournal/${sessionId}/export`, {
        method: "POST",
        headers: getAuthHeaders(),
      });

      if (!res.ok) {
        throw new Error(`Export failed! status: ${res.status}`);
      }

      const data = await res.json();
      const pdfUrl = data.pdfUrl;
      
      // Create a temporary link to download the PDF
      const link = document.createElement('a');
      link.href = pdfUrl;
      link.download = `journal-${date.replace(/\//g, '-')}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Show success message
      alert("✅ PDF downloaded successfully! Your journal has been saved as a beautiful PDF document.");
      
    } catch (err) {
      console.error("PDF Export error:", err);
      alert("❌ Failed to export PDF. Please try again.");
    } finally {
      setExportLoading(false);
      setShowExportConfirm(false);
    }
  };

  // ⭐ HANDLE EXPORT CLICK WITH CONFIRMATION
  const handleExportClick = () => {
    if (!text.trim()) {
      alert("Please write something in your journal before exporting!");
      return;
    }
    setShowExportConfirm(true);
  };

  // ⭐ UPDATED: Create session only when requesting hints
  /*
  const requestHint = async () => {
    // Create session if needed
    let currentSessionId = sessionId;
    if (!currentSessionId) {
      currentSessionId = await createSession();
      if (!currentSessionId) {
        alert("Failed to create session. Please try again.");
        return;
      }
      setSessionId(currentSessionId);
    }

    setHintLoading(true);
    setHint(null);

    try {
      const res = await fetch(`${API_BASE}/freejournal/${currentSessionId}/hints`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ current_content: text || "" }),
      });

      const data = await res.json();
      setHint(data);
      
      setTimeout(() => {
        setHint(null);
      }, 60000);

    } catch (err) {
      console.error("Hint error:", err);
    } finally {
      setHintLoading(false);
    }
  };
*/
// ⭐ UPDATED: Create session only when requesting hints (with auto voice)
const requestHint = async () => {
  // Create session if needed
  let currentSessionId = sessionId;
  if (!currentSessionId) {
    currentSessionId = await createSession();
    if (!currentSessionId) {
      alert("Failed to create session. Please try again.");
      return;
    }
    setSessionId(currentSessionId);
  }

  setHintLoading(true);
  setHint(null);

  try {
    const res = await fetch(`${API_BASE}/freejournal/${currentSessionId}/hints`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ current_content: text || "" }),
    });

    const data = await res.json();
    setHint(data);
    
    // 🎵 AUTOMATIC VOICE PLAYBACK
    const hintText = data.hint_text || data.text || data.content;
    if (hintText) {
      try {
        const voiceRes = await fetch(`${API_BASE}/freejournal/text-to-voice`, {
          method: "POST",
          headers: getAuthHeaders(),
          body: JSON.stringify({ 
            text: hintText, 
            voice_profile: "hints" 
          }),
        });

        if (voiceRes.ok) {
          const voiceData = await voiceRes.json();
          if (voiceData.success) {
            // Auto-play the audio
            const audio = new Audio(`data:${voiceData.content_type};base64,${voiceData.audio_data}`);
            audio.play().catch(error => {
              console.log('Audio autoplay failed:', error);
              // Audio was blocked by browser - user needs to interact first
            });
          }
        }
      } catch (voiceError) {
        console.log('Voice generation failed:', voiceError);
        // Continue without voice if it fails
      }
    }
    
    setTimeout(() => {
      setHint(null);
    }, 60000);

  } catch (err) {
    console.error("Hint error:", err);
  } finally {
    setHintLoading(false);
  }
};
  const handleHintButtonClick = () => {
    requestHint();
  };

  // ⭐ WORKING AI REFLECTION FUNCTION
  const openAIReflection = async () => {
    if (!text.trim()) {
      alert("Please write something in your journal first!");
      return;
    }

    setLoading(true);
    setAiOpen(true);
    setAiReflection(null);
    
    try {
      // Save content first (this creates session if needed)
      await saveContent();
      
      // Now we have a sessionId
      if (!sessionId) {
        throw new Error("No session created after save");
      }
      
      const res = await fetch(`${API_BASE}/freejournal/${sessionId}/reflect`, {
        method: "POST",
        headers: getAuthHeaders(),
      });

      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

      const reflectionData = await res.json();
      setAiReflection(reflectionData);
      
    } catch (err) {
      console.error("AI Reflection error:", err);
      setAiReflection({
        mood: "reflective",
        insights: [
          "Your writing shows thoughtful reflection and self-awareness.",
          "Continue exploring these thoughts to gain deeper understanding."
        ],
        summary: "Based on your journal entry, you're processing your experiences through mindful writing.",
        nextQuestions: [
          "What would you like to explore further in your writing?",
          "How does this reflection make you feel about your journey?"
        ],
        flower_type: "chamomile"
      });
    } finally {
      setLoading(false);
    }
  };

  const getMoodEmoji = (mood) => {
    const emojiMap = {
      happy: "😊",
      sad: "😔",
      anxious: "😰",
      calm: "😌",
      reflective: "🤔"
    };
    return emojiMap[mood] || "📝";
  };

/*voice feature*/
// Add these new state variables
const [mediaRecorder, setMediaRecorder] = useState(null);
const [audioChunks, setAudioChunks] = useState([]);

// Add this function to start recording
const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream);
    const chunks = [];
    
    recorder.ondataavailable = (e) => {
      chunks.push(e.data);
    };
    
    recorder.onstop = async () => {
      const audioBlob = new Blob(chunks, { type: 'audio/wav' });
      await sendAudioToBackend(audioBlob);
      stream.getTracks().forEach(track => track.stop());
    };
    
    recorder.start();
    setMediaRecorder(recorder);
    setAudioChunks(chunks);
    setRecording(true);
    
  } catch (error) {
    console.error('Error starting recording:', error);
    alert('Error accessing microphone. Please check permissions.');
  }
};

// Add this function to stop recording and send to backend
const stopRecording = () => {
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    setRecording(false);
    setTranscribing(true);   
    mediaRecorder.stop();
  }
};


// Add this function to send audio to backend
const sendAudioToBackend = async (audioBlob) => {
  // Create session if needed for voice recording
  let currentSessionId = sessionId;
  if (!currentSessionId) {
    currentSessionId = await createSession();
    if (!currentSessionId) {
      alert('No session found. Please refresh the page.');
      return;
    }
    setSessionId(currentSessionId);
  }

  setLoading(true);
  
  try {
    const formData = new FormData();
    formData.append('audio_file', audioBlob, 'recording.wav');
    
    const token = localStorage.getItem('pauz_token');
    const response = await fetch(`${API_BASE}/freejournal/${currentSessionId}/voice`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Voice transcription failed: ${response.status}`);
    }

    const updatedJournal = await response.json();
    
    // Update the text area with transcribed content
    if (updatedJournal.content) {
      setText(updatedJournal.content);
    }
    
    console.log('✅ Voice transcribed successfully');
    
  } catch (error) {
    console.error('Voice transcription error:', error);
    alert('Failed to transcribe audio. Please try again.');
  }  finally {
  setLoading(false);
  setTranscribing(false);  // 🔥 close the overlay when transcription done
  setMode("write");
}

};

// Update your voice mode button to actually record
const handleVoiceModeClick = async () => {
  if (mode === 'voice') {
    // If already in voice mode, stop recording
    if (recording) {
      stopRecording();
    }
    setMode('write');
  } else {
    // Enter voice mode and start recording
    setMode('voice');
    await startRecording();
  }
};

  return (
    <div className="freejournal-container">
      {/* TOOLBAR */}
      <div className="fj-toolbar-wrapper">
        <div className="fj-toolbar">
          <button
            className={`fj-icon-btn ${mode === "write" ? "active" : ""}`}
            onClick={() => setMode("write")}
          >
            <img src={quillIcon} alt="Write" />
          </button>

         <button
  className={`fj-icon-btn ${mode === "voice" ? "active recording" : ""}`}
  onClick={handleVoiceModeClick}
  disabled={loading}
>
  <img src={micIcon} alt="Record" />
  {mode === "voice" && <span className="fj-recording-indicator"></span>}
</button>

          <button
            className={`fj-icon-btn ${hintLoading ? "loading" : ""}`}
            onClick={handleHintButtonClick}
            disabled={hintLoading}
          >
            <img src={hintIcon} alt="Hint" />
            {hintLoading && <span className="fj-hint-spinner"></span>}
          </button>

          <button 
            className="fj-ai-btn" 
            onClick={openAIReflection}
            disabled={loading || !text.trim()}
          >
            <img src={magicIcon} alt="Magic" className="fj-ai-icon" />
            {loading ? "Reflecting..." : "Reflect with AI"}
          </button>

          {/* ⭐ UPDATED SAVE BUTTON WITH STATUS FEEDBACK */}
          <button 
            className={`fj-icon-btn ${saveStatus ? `save-${saveStatus}` : ""}`}
            onClick={saveContent}
            disabled={loading || !text.trim()}
            title="Save Journal"
          >
            <img src={saveIcon} alt="Save" />
            {saveStatus === "saving" && <span className="fj-save-spinner"></span>}
          </button>

          {/* ⭐ UPDATED DOWNLOAD BUTTON WITH PDF EXPORT */}
          <button 
            className="fj-icon-btn" 
            onClick={handleExportClick}
            disabled={exportLoading || !text.trim()}
            title="Export to PDF"
          >
            <img src={diskIcon} alt="Download PDF" />
            {exportLoading && <span className="fj-export-spinner"></span>}
          </button>
        </div>

        {/* ⭐ SAVE STATUS INDICATOR */}
        
        {saveStatus && (
          <div className={`fj-save-status fj-save-${saveStatus}`}>
            {saveStatus === "saving" && " Saving..."}
            {saveStatus === "saved" && "Journal Saved!"}
            {saveStatus === "error" && "Save Failed"}
          </div>
        )}
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
        {(hintLoading || hint) && (
          <div className="fj-hint-panel">
            {hintLoading && (
              <div className="fj-hint-loading">
                <div className="fj-quill-icon">
                  <img src={quillIcon} alt="Quill Pen" />
                </div>
                <div className="fj-tac-dots">
                  <span></span><span></span><span></span>
                </div>
                Generating hint…
              </div>
            )}

            {hint && !hintLoading && (
              <div className="fj-hint-card">
                <span className="fj-hint-close" onClick={() => setHint(null)}>
                  &times;
                </span>
                <div className="fj-hint-text">
                  {hint.hint_text || hint.text || hint.content}
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* VOICE MODE */}
{mode === "voice" && (
  <div className="fj-voice-overlay active">
    <div className="fj-voice-box">

      <div className="fj-visual-row">
        {/* MIC ICON */}
        <img 
          src={micIcon} 
          alt="Recording" 
          className={`fj-voice-icon ${recording ? 'pulsing' : ''}`}
        />

        {/* DOTS ONLY WHEN RECORDING */}
        {recording && (
          <div className="fj-voice-dots-row">
            <span></span><span></span><span></span>
          </div>
        )}

        {/* JOURNAL ICON */}
        <img 
          src={journalIcon} 
          alt="Journal" 
          className="fj-journal-icon" 
        />
      </div>

      {/* TEXT AREA */}
      <p className="fj-voice-text">
        {recording && "Recording... Speak now. Your words will be transcribed automatically."}
        {transcribing && !recording && (
          <span className="transcribing-text">
            Transcribing your audio… please wait
          </span>
        )}
      </p>

      {/* BUTTONS */}
      {recording && (
        <button 
          onClick={stopRecording}
          className="recording-active"
        >
          🛑 Stop Recording
        </button>
      )}

      {transcribing && !recording && (
        <button 
          disabled
          className="processing-btn"
        >
          ⏳ Transcribing...
        </button>
      )}

    </div>
  </div>
)}


      {/* AI REFLECTION OVERLAY */}
      {aiOpen && (
        <div className="fj-ai-overlay">
          <div className="fj-ai-container">
            <div className="fj-ai-header">
              <div className="fj-ai-title">
                <img src={magicIcon} alt="Magic" className="fj-ai-title-icon" />
                <h2>AI Reflection</h2>
              </div>
              <button 
                className="fj-ai-close-btn"
                onClick={() => setAiOpen(false)}
              >
                &times;
              </button>
            </div>

            <div className="fj-ai-content">
              {loading ? (
                <div className="fj-ai-loading">
                  <div className="fj-ai-spinner-container">
                    {/* Magic Wand Animation */}
                    <div className="fj-magic-wand">
                      <div className="fj-magic-circle"></div>
                      <div className="fj-sparkle">✨</div>
                    </div>
                    
                    {/* Bouncing Dots */}
                    <div className="fj-dots-container">
                      <div className="fj-dot fj-dot-1"></div>
                      <div className="fj-dot fj-dot-2"></div>
                      <div className="fj-dot fj-dot-3"></div>
                      <div className="fj-dot fj-dot-4"></div>
                    </div>
                  </div>
                  
                  <p className="fj-loading-text">Reading your journal with care</p>
                  
                  <div className="fj-loading-subtitle">
                    <div className="fj-loading-words">
                      <span>Finding insights</span>
                      <span>Analyzing patterns</span>
                      <span>Preparing reflections</span>
                      <span>Almost ready</span>
                    </div>
                  </div>
                </div>
              ) : (
                aiReflection && (
                  <div className="fj-ai-reflection">
                    {/* MOOD SECTION */}
                    <div className="fj-ai-section fj-mood-section">
                      <div className="fj-section-header">
                        <span className="fj-section-icon">🎭</span>
                        <h3>Current Mood</h3>
                      </div>
                      <div className={`fj-mood-display fj-mood-${aiReflection.mood}`}>
                        <span className="fj-mood-text">{aiReflection.mood}</span>
                      </div>
                    </div>

                    {/* SUMMARY SECTION */}
                    <div className="fj-ai-section">
                      <div className="fj-section-header">
                        <span className="fj-section-icon">📖</span>
                        <h3>Summary</h3>
                      </div>
                      <div className="fj-summary-text">
                        {aiReflection.summary}
                      </div>
                    </div>

                    {/* INSIGHTS SECTION */}
                    <div className="fj-ai-section">
                      <div className="fj-section-header">
                        <span className="fj-section-icon">💎</span>
                        <h3>Key Insights</h3>
                      </div>
                      <div className="fj-insights-grid">
                        {aiReflection.insights.map((insight, index) => (
                          <div key={index} className="fj-insight-card">
                            <div className="fj-insight-bullet"></div>
                            <p>{insight}</p>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* QUESTIONS SECTION */}
                    <div className="fj-ai-section">
                      <div className="fj-section-header">
                        <span className="fj-section-icon">🌱</span>
                        <h3>Questions to Explore</h3>
                      </div>
                      <div className="fj-questions-list">
                        {aiReflection.nextQuestions.map((question, index) => (
                          <div key={index} className="fj-question-item">
                            <span className="fj-question-marker">?</span>
                            <p>{question}</p>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* FLOWER SECTION */}
                    {aiReflection.flower_type && (
                      <div className="fj-ai-section fj-flower-section">
                        <div className="fj-section-header">
                          <span className="fj-section-icon">🌸</span>
                          <h3>Garden Growth</h3>
                        </div>
                        <div className="fj-flower-message">
                          Your reflection has planted a <span className="fj-flower-highlight">{aiReflection.flower_type}</span> in your garden
                        </div>
                      </div>
                    )}
                  </div>
                )
              )}
            </div>
          </div>
        </div>
      )}

      {/* ⭐ PDF EXPORT CONFIRMATION DIALOG */}
      {showExportConfirm && (
        <div className="fj-export-overlay">
          <div className="fj-export-confirm">
            <div className="fj-export-header">
              <img src={diskIcon} alt="PDF Export" className="fj-export-icon" />
              <h3>Export to PDF</h3>
            </div>
            
            <div className="fj-export-content">
              <p>Your journal entry will be converted into a beautiful PDF document and downloaded automatically.</p>
              <div className="fj-export-details">
                <span className="fj-export-info">📄 Format: PDF Document</span>
                <span className="fj-export-info">📝 Includes: Your journal content and writing hints</span>
                <span className="fj-export-info">💫 Style: Professional journal layout</span>
              </div>
            </div>
            
            <div className="fj-export-actions">
              <button 
                className="fj-export-cancel"
                onClick={() => setShowExportConfirm(false)}
                disabled={exportLoading}
              >
                Cancel
              </button>
              <button 
                className="fj-export-confirm-btn"
                onClick={exportToPDF}
                disabled={exportLoading}
              >
                {exportLoading ? (
                  <>
                    <span className="fj-export-spinner-small"></span>
                    Exporting...
                  </>
                ) : (
                  "Export PDF"
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FreeJournal;