// Garden API utilities

const API_BASE_URL = process.env.REACT_APP_API_URL || '';

export const gardenAPI = {
  // Fetch all garden entries for the current user
  async getGardenEntries() {
    const response = await fetch(`${API_BASE_URL}/garden/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to fetch garden entries');
    }

    const data = await response.json();
    return data.map(entry => ({
      id: entry.id,
      mood: entry.mood,
      date: new Date(entry.created_at).toISOString().split('T')[0],
      note: entry.note || 'No note saved.'
    }));
  },

  // Create a new garden entry (this is automatically called by reflect_with_ai)
  async createGardenEntry(mood, note) {
    const response = await fetch(`${API_BASE_URL}/garden/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
      },
      body: JSON.stringify({
        mood: mood,
        note: note,
        flower_type: mood // Backend expects same mood as flower_type
      })
    });

    if (!response.ok) {
      throw new Error('Failed to create garden entry');
    }

    return await response.json();
  }
};

// Free Journal API utilities (for reflect with AI)
export const freeJournalAPI = {
  // Trigger AI reflection for a journal session
  async reflectWithAI(sessionId) {
    const response = await fetch(`${API_BASE_URL}/freejournal/${sessionId}/reflect`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to reflect with AI');
    }

    const data = await response.json();
    return {
      mood: data.mood,
      insights: data.insights,
      summary: data.summary,
      nextQuestions: data.nextQuestions,
      flowerType: data.flower_type
    };
  }
};