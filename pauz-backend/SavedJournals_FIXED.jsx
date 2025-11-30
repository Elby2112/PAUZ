// SavedJournals.jsx - FIXED VERSION
import React, { useState, useEffect } from "react";
import "../styles/savedJournals.css";

const API_BASE = "http://localhost:8000";

const getAuthHeaders = () => {
  const token = localStorage.getItem("pauz_token");
  console.log("🔑 Token exists:", !!token);
  if (!token) return {};
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
};

const SavedJournals = () => {
  const [journals, setJournals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedJournal, setSelectedJournal] = useState(null);
  const [showJournalModal, setShowJournalModal] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log("🚀 SavedJournals component mounted");
    fetchJournals();
  }, []);

  const fetchJournals = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log("📚 Fetching user journals from:", `${API_BASE}/freejournal/`);
      
      const headers = getAuthHeaders();
      console.log("📋 Request headers:", headers);
      
      const res = await fetch(`${API_BASE}/freejournal/`, {
        method: "GET",
        headers: headers,
      });

      console.log("📊 Response status:", res.status);
      console.log("📊 Response ok:", res.ok);
      
      if (res.ok) {
        const journalsData = await res.json();
        console.log("✅ Journals fetched successfully. Count:", journalsData.length);
        console.log("📄 Journals data:", journalsData);
        
        if (journalsData.length === 0) {
          console.log("📝 No journals found in database");
        }
        
        // Transform the backend data
        const journalsWithThemes = journalsData.map((journal, index) => {
          let title = `Journal ${formatDate(journal.created_at)}`;
          if (journal.content && journal.content.trim()) {
            const firstWords = journal.content.split(' ').slice(0, 3).join(' ');
            if (firstWords.length > 5) {
              title = firstWords + '...';
            }
          }
          
          const colors = ["purple", "beige", "lavender", "rose", "blue", "green"];
          const coverColor = colors[index % colors.length];
          
          return {
            ...journal,
            title: title,
            coverColor: coverColor,
            type: "Free Journal"
          };
        });
        
        setJournals(journalsWithThemes);
      } else {
        console.error("❌ Failed to fetch journals, status:", res.status);
        const errorText = await res.text();
        console.error("❌ Error response:", errorText);
        setError(`Failed to fetch journals: ${res.status}`);
        setJournals([]);
      }
    } catch (err) {
      console.error("❌ Error fetching journals:", err);
      setError(`Network error: ${err.message}`);
      setJournals([]);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-GB", {
      day: "numeric",
      month: "short", 
      year: "numeric"
    });
  };

  const openJournal = (journal) => {
    setSelectedJournal(journal);
    setShowJournalModal(true);
  };

  const closeJournal = () => {
    setShowJournalModal(false);
    setSelectedJournal(null);
  };

  // Add a refresh button for testing
  const handleRefresh = () => {
    console.log("🔄 Manually refreshing journals...");
    fetchJournals();
  };

  // Delete journal function
  const deleteJournal = async (journalId) => {
    if (!window.confirm("Are you sure you want to delete this journal?")) {
      return;
    }

    try {
      const headers = getAuthHeaders();
      const res = await fetch(`${API_BASE}/freejournal/${journalId}`, {
        method: "DELETE",
        headers: headers,
      });

      if (res.ok) {
        console.log("✅ Journal deleted successfully");
        // Remove from local state
        setJournals(journals.filter(j => j.id !== journalId));
        // Close modal if it was the selected journal
        if (selectedJournal && selectedJournal.id === journalId) {
          closeJournal();
        }
      } else {
        console.error("❌ Failed to delete journal");
        alert("Failed to delete journal");
      }
    } catch (err) {
      console.error("❌ Error deleting journal:", err);
      alert("Error deleting journal");
    }
  };

  if (loading) {
    return (
      <div className="saved-journals-container">
        <div className="sj-loading">
          <div className="sj-spinner"></div>
          <p>Loading your journals...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="saved-journals-container">
      {/* Header with Refresh Button */}
      <div className="sj-header">
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
          <div>
            <h1>My Journal Collection</h1>
            <p>Your personal library of thoughts and reflections</p>
          </div>
          <button 
            className="sj-refresh-btn"
            onClick={handleRefresh}
            style={{
              background: '#8c6e94',
              color: 'white',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '8px',
              cursor: 'pointer',
              marginRight: '1rem'
            }}
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div style={{
          background: '#f8d7da',
          color: '#721c24',
          padding: '1rem',
          borderRadius: '8px',
          marginBottom: '2rem',
          border: '1px solid #f5c6cb'
        }}>
          <h4>Error:</h4>
          <p>{error}</p>
          <button onClick={fetchJournals} style={{
            background: '#721c24',
            color: 'white',
            border: 'none',
            padding: '0.5rem 1rem',
            borderRadius: '4px',
            cursor: 'pointer'
          }}>
            Try Again
          </button>
        </div>
      )}

      {/* Debug Info */}
      <div style={{
        background: '#f8f9fa',
        padding: '1rem',
        borderRadius: '8px',
        marginBottom: '2rem',
        border: '1px solid #e9ecef'
      }}>
        <h4>Debug Information:</h4>
        <p>📊 Journals found: <strong>{journals.length}</strong></p>
        <p>🔑 User authenticated: <strong>{localStorage.getItem('pauz_token') ? 'Yes' : 'No'}</strong></p>
        <p>🌐 API Base: <strong>{API_BASE}</strong></p>
        {journals.length > 0 && (
          <p>📝 Latest journal: <strong>{journals[0].title}</strong></p>
        )}
      </div>

      {/* Journals Shelf */}
      {journals.length === 0 ? (
        <div className="sj-empty">
          <div className="sj-empty-icon">📝</div>
          <h3>No journals yet</h3>
          <p>Start writing in your Free Journal to see your entries here</p>
          <p style={{color: '#666', fontSize: '0.9rem', marginTop: '1rem'}}>
            Make sure to click the save button after writing!
          </p>
          <button 
            className="sj-start-writing-btn"
            onClick={() => window.location.href = '/journal'}
          >
            Start Writing
          </button>
        </div>
      ) : (
        <div className="sj-shelf">
          <div className="sj-shelf-surface"></div>
          <div className="sj-books-grid">
            {journals.map((journal, index) => (
              <div
                key={journal.id || journal.session_id || index}
                className={`sj-book sj-book-${journal.coverColor}`}
                onClick={() => openJournal(journal)}
                style={{ position: 'relative' }}
              >
                <div className="sj-book-spine">
                  <div className="sj-book-title">{journal.title}</div>
                  <div className="sj-book-date">{formatDate(journal.created_at)}</div>
                </div>
                <div className="sj-book-cover">
                  <div className="sj-book-cover-content">
                    <h3>{journal.title}</h3>
                    <span className="sj-book-type">{journal.type}</span>
                    <span className="sj-book-hint">Click to read</span>
                  </div>
                </div>
                {/* Delete button */}
                <button
                  className="sj-delete-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteJournal(journal.id);
                  }}
                  style={{
                    position: 'absolute',
                    top: '5px',
                    right: '5px',
                    background: '#dc3545',
                    color: 'white',
                    border: 'none',
                    borderRadius: '50%',
                    width: '20px',
                    height: '20px',
                    cursor: 'pointer',
                    fontSize: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                  title="Delete journal"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Journal Reading Modal */}
      {showJournalModal && selectedJournal && (
        <div className="sj-journal-modal-overlay">
          <div className="sj-journal-modal">
            <div className="sj-journal-pages">
              {/* Left Page */}
              <div className="sj-journal-page sj-left-page">
                <div className="sj-page-content">
                  <div className="sj-journal-header">
                    <h2>{selectedJournal.title}</h2>
                    <div className="sj-journal-meta">
                      <span className="sj-journal-type">{selectedJournal.type}</span>
                      <span className="sj-journal-date">{formatDate(selectedJournal.created_at)}</span>
                    </div>
                    <div className="sj-journal-stats">
                      <p>📝 Words: {selectedJournal.content ? selectedJournal.content.split(' ').length : 0}</p>
                      <p>📄 Lines: {selectedJournal.content ? selectedJournal.content.split('\n').length : 0}</p>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Right Page */}
              <div className="sj-journal-page sj-right-page">
                <div className="sj-page-content">
                  <div className="sj-journal-text">
                    {selectedJournal.content && selectedJournal.content.trim() ? (
                      selectedJournal.content.split('\n').map((paragraph, index) => (
                        <p key={index} style={{ marginBottom: '1rem' }}>
                          {paragraph.trim() ? paragraph : '\u00A0'}
                        </p>
                      ))
                    ) : (
                      <p style={{ fontStyle: 'italic', color: '#666' }}>
                        This journal is empty. Start writing to see your content here.
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>
            
            <div className="sj-journal-actions">
              <button className="sj-close-journal-btn" onClick={closeJournal}>
                Close Journal
              </button>
              <button 
                className="sj-delete-modal-btn"
                onClick={() => {
                  if (window.confirm("Delete this journal?")) {
                    deleteJournal(selectedJournal.id);
                  }
                }}
                style={{
                  background: '#dc3545',
                  color: 'white',
                  border: 'none',
                  padding: '0.5rem 1rem',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  marginLeft: '1rem'
                }}
              >
                🗑️ Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SavedJournals;