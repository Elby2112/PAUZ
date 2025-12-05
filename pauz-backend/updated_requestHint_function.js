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
        const voiceRes = await fetch(`${API_BASE}/free-journal/text-to-voice`, {
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