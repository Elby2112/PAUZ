// SavedJournals.jsx - ENHANCED WITH FILTERING & FIXED DELETE
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
  const [filteredJournals, setFilteredJournals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedJournal, setSelectedJournal] = useState(null);
  const [showJournalModal, setShowJournalModal] = useState(false);
  const [error, setError] = useState(null);

  // Filter states
  const [searchTerm, setSearchTerm] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState("desc");
  const [limit, setLimit] = useState("");

  useEffect(() => {
    console.log("🚀 SavedJournals component mounted");
    fetchJournals();
  }, []);

  // Apply filters when journals or filter criteria change
  useEffect(() => {
    if (journals.length > 0) {
      applyFilters();
    } else {
      setFilteredJournals([]);
    }
  }, [journals, searchTerm, startDate, endDate, sortBy, sortOrder, limit]);

  const fetchJournals = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams();
      if (startDate) params.append("start_date", startDate);
      if (endDate) params.append("end_date", endDate);
      if (searchTerm) params.append("search", searchTerm);
      if (limit) params.append("limit", limit);
      if (sortBy) params.append("sort_by", sortBy);
      if (sortOrder) params.append("order", sortOrder);

      const url = `${API_BASE}/freejournal/?${params.toString()}`;
      console.log("📚 Fetching user journals from:", url);
      
      const headers = getAuthHeaders();
      
      const res = await fetch(url, {
        method: "GET",
        headers: headers,
      });

      console.log("📊 Response status:", res.status);
      
      if (res.ok) {
        const journalsData = await res.json();
        console.log("✅ Journals fetched successfully. Count:", journalsData.length);
        
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
        setFilteredJournals(journalsWithThemes);
      } else {
        console.error("❌ Failed to fetch journals, status:", res.status);
        const errorText = await res.text();
        console.error("❌ Error response:", errorText);
        setError(`Failed to fetch journals: ${res.status}`);
        setJournals([]);
        setFilteredJournals([]);
      }
    } catch (err) {
      console.error("❌ Error fetching journals:", err);
      setError(`Network error: ${err.message}`);
      setJournals([]);
      setFilteredJournals([]);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...journals];

    // Client-side search (in addition to server-side)
    if (searchTerm && !searchTerm.includes('&search=')) {
      filtered = filtered.filter(journal => 
        journal.content && journal.content.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Client-side date filtering (in addition to server-side)
    if (startDate && !startDate.includes('&start_date=')) {
      filtered = filtered.filter(journal => 
        new Date(journal.created_at) >= new Date(startDate)
      );
    }

    if (endDate && !endDate.includes('&end_date=')) {
      filtered = filtered.filter(journal => 
        new Date(journal.created_at) <= new Date(endDate + 'T23:59:59')
      );
    }

    // Client-side sorting
    filtered.sort((a, b) => {
      const aValue = a[sortBy];
      const bValue = b[sortBy];
      
      if (sortOrder === "asc") {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    // Apply limit
    if (limit && !limit.includes('&limit=')) {
      filtered = filtered.slice(0, parseInt(limit));
    }

    setFilteredJournals(filtered);
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

  const handleRefresh = () => {
    console.log("🔄 Manually refreshing journals...");
    fetchJournals();
  };

  // FIXED: Delete journal using session_id instead of id
  const deleteJournal = async (journal) => {
    if (!window.confirm("Are you sure you want to delete this journal?")) {
      return;
    }

    try {
      console.log("🗑️ Deleting journal with session_id:", journal.session_id);
      
      const headers = getAuthHeaders();
      const res = await fetch(`${API_BASE}/freejournal/${journal.session_id}`, {
        method: "DELETE",
        headers: headers,
      });

      if (res.ok) {
        console.log("✅ Journal deleted successfully");
        // Remove from local state
        setJournals(journals.filter(j => j.session_id !== journal.session_id));
        // Close modal if it was the selected journal
        if (selectedJournal && selectedJournal.session_id === journal.session_id) {
          closeJournal();
        }
      } else {
        console.error("❌ Failed to delete journal, status:", res.status);
        const errorText = await res.text();
        console.error("❌ Error response:", errorText);
        alert(`Failed to delete journal: ${res.status}`);
      }
    } catch (err) {
      console.error("❌ Error deleting journal:", err);
      alert("Error deleting journal");
    }
  };

  const clearFilters = () => {
    setSearchTerm("");
    setStartDate("");
    setEndDate("");
    setSortBy("created_at");
    setSortOrder("desc");
    setLimit("");
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

      {/* FILTERS SECTION */}
      <div style={{
        background: '#f8f9fa',
        padding: '1.5rem',
        borderRadius: '8px',
        marginBottom: '2rem',
        border: '1px solid #e9ecef'
      }}>
        <h3>🔍 Filters & Search</h3>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
          {/* Search */}
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
              Search Content:
            </label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search in journal content..."
              style={{
                width: '100%',
                padding: '0.5rem',
                border: '1px solid #ddd',
                borderRadius: '4px'
              }}
            />
          </div>

          {/* Start Date */}
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
              From Date:
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              style={{
                width: '100%',
                padding: '0.5rem',
                border: '1px solid #ddd',
                borderRadius: '4px'
              }}
            />
          </div>

          {/* End Date */}
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
              To Date:
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              style={{
                width: '100%',
                padding: '0.5rem',
                border: '1px solid #ddd',
                borderRadius: '4px'
              }}
            />
          </div>

          {/* Sort By */}
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
              Sort By:
            </label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              style={{
                width: '100%',
                padding: '0.5rem',
                border: '1px solid #ddd',
                borderRadius: '4px'
              }}
            >
              <option value="created_at">Date Created</option>
              <option value="id">ID</option>
            </select>
          </div>

          {/* Sort Order */}
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
              Order:
            </label>
            <select
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value)}
              style={{
                width: '100%',
                padding: '0.5rem',
                border: '1px solid #ddd',
                borderRadius: '4px'
              }}
            >
              <option value="desc">Newest First</option>
              <option value="asc">Oldest First</option>
            </select>
          </div>

          {/* Limit */}
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
              Limit:
            </label>
            <input
              type="number"
              value={limit}
              onChange={(e) => setLimit(e.target.value)}
              placeholder="Max results..."
              min="1"
              style={{
                width: '100%',
                padding: '0.5rem',
                border: '1px solid #ddd',
                borderRadius: '4px'
              }}
            />
          </div>
        </div>

        {/* Filter Actions */}
        <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem' }}>
          <button
            onClick={clearFilters}
            style={{
              background: '#6c757d',
              color: 'white',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Clear Filters
          </button>
          <span style={{ 
            color: '#666', 
            display: 'flex',
            alignItems: 'center',
            fontWeight: 'bold'
          }}>
            Showing {filteredJournals.length} of {journals.length} journals
          </span>
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
        <p>📊 Total journals: <strong>{journals.length}</strong></p>
        <p>🔍 Filtered journals: <strong>{filteredJournals.length}</strong></p>
        <p>🔑 User authenticated: <strong>{localStorage.getItem('pauz_token') ? 'Yes' : 'No'}</strong></p>
        <p>🌐 API Base: <strong>{API_BASE}</strong></p>
        {filteredJournals.length > 0 && (
          <p>📝 Latest journal: <strong>{filteredJournals[0].title}</strong></p>
        )}
      </div>

      {/* Journals Shelf */}
      {filteredJournals.length === 0 ? (
        <div className="sj-empty">
          <div className="sj-empty-icon">📝</div>
          <h3>
            {journals.length === 0 ? "No journals yet" : "No journals match your filters"}
          </h3>
          <p>
            {journals.length === 0 
              ? "Start writing in your Free Journal to see your entries here"
              : "Try adjusting your filters or clear them to see all journals"
            }
          </p>
          {journals.length === 0 && (
            <>
              <p style={{color: '#666', fontSize: '0.9rem', marginTop: '1rem'}}>
                Make sure to click the save button after writing!
              </p>
              <button 
                className="sj-start-writing-btn"
                onClick={() => window.location.href = '/journal'}
              >
                Start Writing
              </button>
            </>
          )}
        </div>
      ) : (
        <div className="sj-shelf">
          <div className="sj-shelf-surface"></div>
          <div className="sj-books-grid">
            {filteredJournals.map((journal, index) => (
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
                    deleteJournal(journal);
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
                      <p>🆔 Session: {selectedJournal.session_id}</p>
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
                onClick={() => deleteJournal(selectedJournal)}
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