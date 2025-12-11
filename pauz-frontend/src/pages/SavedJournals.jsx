// SavedJournals.jsx - FIXED VERSION WITH GUIDED JOURNAL CONTENT FIX
import React, { useEffect, useMemo, useState } from "react";
import "../styles/savedJournals.css";

//const API_BASE = "http://localhost:8000";
const API_BASE="http://155.138.238.152:8000"

const getAuthHeaders = () => {
  const token = localStorage.getItem("pauz_token");
  if (!token) return {};
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
};

const Toast = ({ message, type = "success", onClose }) => {
  if (!message) return null;
  return (
    <div className={`sj-toast sj-toast-${type}`} role="status" aria-live="polite">
      <div className="sj-toast-inner">
        <span className="sj-toast-icon">{type === "success" ? "✅" : "⚠️"}</span>
        <div className="sj-toast-msg">{message}</div>
        <button className="sj-toast-close" onClick={onClose} aria-label="Close notification">✕</button>
      </div>
    </div>
  );
};

const SavedJournals = () => {
  const [journals, setJournals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedJournal, setSelectedJournal] = useState(null);
  const [showJournalModal, setShowJournalModal] = useState(false);
  const [toast, setToast] = useState({ message: "", type: "success" });

  // Filters / UI state
  const [query, setQuery] = useState("");
  const [filterType, setFilterType] = useState("all"); // all | free | guided
  const [sortBy, setSortBy] = useState("newest"); // newest | oldest | title

  useEffect(() => {
    fetchJournals();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const showToast = (message, type = "success", duration = 3200) => {
    setToast({ message, type });
    if (duration > 0) {
      setTimeout(() => setToast({ message: "", type: "success" }), duration);
    }
  };

  const fetchJournals = async () => {
  setLoading(true);
  try {
    const headers = getAuthHeaders();
    console.log('🔍 Fetching journals with headers:', headers);

    // ADD ?previews_only=false TO GET FULL CONTENT
    const [freeRes, guidedRes] = await Promise.all([
      fetch(`${API_BASE}/freejournal/?previews_only=false`, { method: "GET", headers }),
      fetch(`${API_BASE}/guided_journal/?previews_only=false`, { method: "GET", headers }),
    ]);

    console.log('📡 Free journal response status:', freeRes.status);
    console.log('📡 Guided journal response status:', guidedRes.status);

    const all = [];
    
    // ... rest of your code

      // Process free journals
      if (freeRes.ok) {
        const freeData = await freeRes.json();
        console.log('✅ Free journals loaded:', freeData.length, 'items');
        freeData.forEach((j, i) => {
          const journalContent = j.content_preview || j.content || "";
          const titleFromContent = journalContent && journalContent.trim()
            ? journalContent.split(" ").slice(0, 6).join(" ")
            : "";
          all.push({
            ...j,
            type: "Free Journal",
            title: titleFromContent || `Free Journal · ${formatDate(j.created_at)}`,
            identifier: j.session_id || j.id,
            coverTone: ["warm-beige", "sage", "lavender"][i % 3],
            created_at: j.created_at || new Date().toISOString(),
            content: journalContent,
          });
        });
      } else {
        console.log('❌ Free journals failed:', freeRes.status);
        const errorText = await freeRes.text();
        console.log('Free journals error:', errorText);
      }

      // Process guided journals - UPDATED FIX FOR CONTENT DISPLAY
      if (guidedRes.ok) {
        const gdata = await guidedRes.json();
        console.log('✅ Guided journals loaded:', gdata.length, 'items');
        
        // DEBUG: Check actual data structure
        if (gdata.length > 0) {
          console.log('🔍 FIRST GUIDED JOURNAL DATA STRUCTURE:', Object.keys(gdata[0]));
          console.log('🔍 Does it have entries?', gdata[0]?.entries);
          console.log('🔍 Does it have prompts?', gdata[0]?.prompts);
          console.log('🔍 Sample entry:', gdata[0]?.entries?.[0]);
          console.log('🔍 Sample prompt:', gdata[0]?.prompts?.[0]);
        }
        
        if (gdata.length === 0) {
          console.log('⚠️ No guided journals found');
        }
        
        gdata.forEach((j, i) => {
          console.log(`📝 Processing guided journal ${i}:`, {
            id: j.id,
            topic: j.topic,
            entriesCount: j.entries?.length || 0,
            promptsCount: j.prompts?.length || 0
          });
          
          let guidedContent = "";
          let entries = [];
          let prompts = j.prompts || [];
          
          // NEW FIX: Properly combine prompts with entries
          if (j.entries && Array.isArray(j.entries) && prompts.length > 0) {
            entries = j.entries;
            
            // Create a map for quick prompt lookup: prompt_id -> prompt_text
            const promptMap = {};
            prompts.forEach(prompt => {
              promptMap[prompt.id] = prompt.text;
            });
            
            // Build content by matching entries with prompts
            guidedContent = j.entries.map(entry => {
              const promptText = promptMap[entry.prompt_id] || `Prompt ${entry.prompt_id}`;
              return `${promptText}:\n${entry.response || ''}`;
            }).join('\n\n');
            
            console.log(`📋 Combined ${entries.length} entries with ${prompts.length} prompts`);
            
          } else if (j.entries && Array.isArray(j.entries)) {
            // Fallback if we have entries but no prompts
            entries = j.entries;
            guidedContent = j.entries.map(entry => 
              `Prompt ${entry.prompt_id || '?'}:\n${entry.response || ''}`
            ).join('\n\n');
            console.log(`📋 Using entries only (no prompts): ${entries.length} entries`);
            
          } else if (j.answers && Array.isArray(j.answers)) {
            // Old structure: answers array
            entries = j.answers.map((answer, idx) => ({
              prompt_id: idx + 1,
              response: answer,
              prompt_text: prompts[idx] ? prompts[idx].text : `Question ${idx + 1}`
            }));
            guidedContent = j.answers.join('\n\n');
            console.log(`📋 Using answers structure: ${j.answers.length} answers`);
            
          } else {
            // No entries found
            guidedContent = j.content || j.description || `Guided journal on topic: ${j.topic || 'Unknown'}`;
            console.log('📋 No entries found, using fallback');
          }
          
          const journalItem = {
            ...j,
            type: "Guided Journal",
            title: j.topic ? `Guided: ${j.topic}` : `Guided Journal · ${formatDate(j.created_at)}`,
            identifier: j.id || j.journal_id || j.guided_journal_id,
            coverTone: ["rose", "blue", "olive"][i % 3],
            created_at: j.created_at || new Date().toISOString(),
            content: guidedContent,
            entries: entries,
            prompts: prompts, // Store prompts for modal display
          };
          
          console.log(`✅ Processed guided journal:`, journalItem.title);
          all.push(journalItem);
        });
      } else {
        console.log('❌ Guided journals failed:', guidedRes.status);
        const errorText = await guidedRes.text();
        console.log('Guided journals error:', errorText);
      }

      // sort newest first by default
      all.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      console.log('📚 Final combined journals:', all.length, 'items');
      console.log('📊 Journal types:', all.reduce((acc, j) => {
        acc[j.type] = (acc[j.type] || 0) + 1;
        return acc;
      }, {}));
      
      setJournals(all);
    } catch (err) {
      console.error("💥 Fetch error:", err);
      showToast("Unable to load journals — check your network or login.", "error", 5000);
      setJournals([]);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (s) => {
    if (!s) return "";
    const d = new Date(s);
    return d.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
  };

  const openJournal = (j) => {
    console.log('📖 Opening journal:', {
      title: j.title,
      type: j.type,
      entriesCount: j.entries?.length || 0,
      promptsCount: j.prompts?.length || 0
    });
    setSelectedJournal(j);
    setShowJournalModal(true);
    document.body.style.overflow = "hidden";
  };

  const closeJournal = () => {
    setShowJournalModal(false);
    setSelectedJournal(null);
    document.body.style.overflow = "";
  };

  const deleteJournal = async (journal, e) => {
    e && e.stopPropagation();
    const confirmMsg = `Delete "${journal.title}"? This cannot be undone.`;
    if (!window.confirm(confirmMsg)) return;

    const headers = getAuthHeaders();
    try {
      let endpoint;
      if (journal.type === "Guided Journal") {
        endpoint = `${API_BASE}/guided_journal/${journal.identifier}`;
      } else {
        endpoint = `${API_BASE}/freejournal/${journal.identifier}`;
      }

      console.log('🗑️ Deleting journal:', journal.type, journal.identifier);

      setJournals((prev) => prev.map((j) => (j.identifier === journal.identifier ? { ...j, deleting: true } : j)));

      const res = await fetch(endpoint, { method: "DELETE", headers });
      if (res.ok) {
        setJournals((prev) => prev.filter((j) => j.identifier !== journal.identifier));
        if (selectedJournal?.identifier === journal.identifier) closeJournal();
        showToast(`"${journal.title}" deleted.`, "success");
        console.log('✅ Journal deleted successfully');
      } else {
        const text = await res.text().catch(() => "");
        console.log('❌ Delete failed:', res.status, text);
        showToast(`Failed to delete (${res.status}) ${text}`, "error", 6000);
        setJournals((prev) => prev.map((j) => (j.identifier === journal.identifier ? { ...j, deleting: false } : j)));
      }
    } catch (err) {
      console.error("💥 Delete error:", err);
      showToast("Network error while deleting journal.", "error", 6000);
      setJournals((prev) => prev.map((j) => (j.identifier === journal.identifier ? { ...j, deleting: false } : j)));
    }
  };

  const filteredJournals = useMemo(() => {
    const q = query.trim().toLowerCase();
    let list = journals.slice();

    if (filterType === "free") list = list.filter((j) => j.type === "Free Journal");
    if (filterType === "guided") list = list.filter((j) => j.type === "Guided Journal");

    if (q) {
      list = list.filter((j) => {
        const txt = `${j.title} ${j.content || ""} ${j.type}`.toLowerCase();
        return txt.includes(q);
      });
    }

    if (sortBy === "title") {
      list.sort((a, b) => a.title.localeCompare(b.title));
    } else if (sortBy === "oldest") {
      list.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
    } else {
      list.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    }

    return list;
  }, [journals, query, filterType, sortBy]);

  return (
    <div className="saved-journals-container">
      <header className="sj-header">
        <div className="sj-head-left">
          <h1 className="sj-title">My Journals</h1>
          <p className="sj-sub">A calm shelf of your moments, prompts and reflections</p>
          {/* Debug info - remove in production */}
          <small style={{color: '#666'}}>
            Found: {journals.filter(j => j.type === 'Guided Journal').length} guided, {journals.filter(j => j.type === 'Free Journal').length} free
          </small>
        </div>

        <div className="sj-controls">
          <div className="sj-search">
            <input
              placeholder="Search by title or content..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              aria-label="Search journals"
            />
            <button
              className="sj-refresh"
              title="Refresh"
              onClick={fetchJournals}
              aria-label="Refresh journals"
            >
              ↻
            </button>
          </div>

          <div className="sj-filter-row">
            <select value={filterType} onChange={(e) => setFilterType(e.target.value)} aria-label="Filter journal type">
              <option value="all">All</option>
              <option value="free">Free</option>
              <option value="guided">Guided</option>
            </select>

            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} aria-label="Sort journals">
              <option value="newest">Newest first</option>
              <option value="oldest">Oldest first</option>
              <option value="title">Title A → Z</option>
            </select>
          </div>
        </div>
      </header>

      <main className="sj-main">
        {loading ? (
          <div className="sj-loading">
            <div className="sj-spinner" aria-hidden />
            <p>Gathering your pages…</p>
          </div>
        ) : filteredJournals.length === 0 ? (
          <div className="sj-empty">
            <div className="sj-empty-illustration">📓</div>
            <h3>No journals found</h3>
            <p>Write something new or adjust your search / filter.</p>
            <div className="sj-empty-actions">
              <button onClick={() => (window.location.href = "/journal")} className="sj-action">New Free Journal</button>
              <button onClick={() => (window.location.href = "/guided-journal")} className="sj-action sj-action-soft">Try Guided</button>
            </div>
          </div>
        ) : (
          <section className="sj-grid" role="list">
            {filteredJournals.map((j) => (
              <article
                key={j.identifier}
                role="listitem"
                className={`sj-card sj-tone-${j.coverTone} ${j.deleting ? "sj-card-deleting" : ""}`}
                onClick={() => openJournal(j)}
                aria-label={`Open ${j.title}`}
              >
                <div className="sj-card-spine" aria-hidden>
                  <div className="sj-spine-title">
                    <span>{j.type === "Free Journal" ? "Free" : "Guided"}</span>
                  </div>
                </div>

                <div className="sj-card-cover">
                  <div className="sj-card-top">
                    <div className="sj-card-title">{j.title}</div>
                    <div className="sj-card-date">{formatDate(j.created_at)}</div>
                  </div>

                  <div className="sj-card-preview">
                    <p>{(j.content || "").slice(0, 130) || "No content — open to start writing."}</p>
                  </div>

                  <div className="sj-card-footer">
                    <span className="sj-badge">{j.type}</span>
                    <div className="sj-actions">
                      <button
                        className="sj-delete-btn-small"
                        onClick={(e) => deleteJournal(j, e)}
                        title={`Delete ${j.title}`}
                        aria-label={`Delete ${j.title}`}
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                </div>
              </article>
            ))}
          </section>
        )}
      </main>

      {/* Modal - UPDATED for guided journals content display */}
      {showJournalModal && selectedJournal && (
        <div className="sj-modal-overlay" onClick={closeJournal} role="dialog" aria-modal="true">
          <div className="sj-modal" onClick={(e) => e.stopPropagation()}>
            <div className="sj-notebook">
              <aside className="sj-left-notebook">
                <header>
                  <h2>{selectedJournal.title}</h2>
                  <div className="sj-modal-meta">
                    <span>{selectedJournal.type}</span>
                    <span>•</span>
                    <time>{formatDate(selectedJournal.created_at)}</time>
                  </div>
                </header>

                <section className="sj-stats">
                  <div>Words: {(selectedJournal.content || "").split(/\s+/).filter(Boolean).length}</div>
                  <div>Lines: {(selectedJournal.content || "").split("\n").filter(Boolean).length}</div>
                  {selectedJournal.type === "Guided Journal" && (
                    <div>Entries: {(selectedJournal.entries || []).length}</div>
                  )}
                </section>
              </aside>

              <section className="sj-right-notebook">
                <div className="sj-article">
                  {selectedJournal.type === "Guided Journal" && selectedJournal.entries && selectedJournal.entries.length > 0 ? (
                    selectedJournal.entries.map((entry, idx) => {
                      // Get prompt text from prompts array if available
                      let promptText = entry.prompt_text || entry.prompt;
                      
                      if (!promptText && selectedJournal.prompts && Array.isArray(selectedJournal.prompts)) {
                        const prompt = selectedJournal.prompts.find(p => p.id === entry.prompt_id);
                        promptText = prompt ? prompt.text : `Prompt ${entry.prompt_id || idx + 1}`;
                      }
                      
                      return (
                        <div key={idx} className="sj-guided-entry">
                          <h4 className="sj-prompt">
                            {promptText || `Prompt ${idx + 1}`}
                          </h4>
                          <p className="sj-para">
                            {entry.response || entry.answer || "No answer provided"}
                          </p>
                        </div>
                      );
                    })
                  ) : (selectedJournal.content && selectedJournal.content.trim()) ? (
                    selectedJournal.content.split("\n").map((p, idx) => (
                      <p key={idx} className="sj-para">{p || "\u00A0"}</p>
                    ))
                  ) : (
                    <div className="sj-empty-journal-copy">
                      <p>This journal has no content yet. Start writing in the journal editor to fill this page.</p>
                    </div>
                  )}
                </div>
              </section>
            </div>

            <footer className="sj-modal-actions">
              <button className="sj-btn" onClick={closeJournal}>Close</button>
              <button
                className="sj-btn sj-danger"
                onClick={() => deleteJournal(selectedJournal)}
              >
                Delete
              </button>
            </footer>
          </div>
        </div>
      )}

      <Toast
        message={toast.message}
        type={toast.type}
        onClose={() => setToast({ message: "", type: "success" })}
      />
    </div>
  );
};

export default SavedJournals;