/**
 * Voice Hints Frontend Integration Example
 * Shows how to add "Read Aloud" functionality to hints in your journaling app
 */

class VoiceHintPlayer {
    constructor() {
        this.audio = new Audio();
        this.currentlyPlaying = null;
    }

    /**
     * Convert hint text to speech and play it
     * @param {string} hintText - The hint text to read aloud
     * @param {string} voiceProfile - Voice profile to use (hints, welcome, guide)
     * @param {HTMLElement} buttonElement - The button that triggered this
     */
    async playHint(hintText, voiceProfile = 'hints', buttonElement) {
        try {
            // Show loading state
            if (buttonElement) {
                buttonElement.disabled = true;
                buttonElement.innerHTML = '🔊 Loading...';
            }

            // Call the voice API
            const response = await fetch('/free-journal/text-to-voice', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // Add your auth headers if needed
                    // 'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    text: hintText,
                    voice_profile: voiceProfile
                })
            });

            if (!response.ok) {
                throw new Error(`Voice API error: ${response.status}`);
            }

            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error || 'Voice generation failed');
            }

            // Create audio blob from base64 data
            const audioBytes = Uint8Array.from(atob(result.audio_data), c => c.charCodeAt(0));
            const audioBlob = new Blob([audioBytes], { type: result.content_type });
            const audioUrl = URL.createObjectURL(audioBlob);

            // Play the audio
            this.audio.src = audioUrl;
            this.audio.play();

            // Update button state
            if (buttonElement) {
                buttonElement.innerHTML = '🔊 Playing...';
                
                // Reset button when audio finishes
                this.audio.onended = () => {
                    buttonElement.disabled = false;
                    buttonElement.innerHTML = '🔊 Read Aloud';
                    this.currentlyPlaying = null;
                    URL.revokeObjectURL(audioUrl); // Clean up
                };
            }

            this.currentlyPlaying = hintText;

        } catch (error) {
            console.error('Error playing hint:', error);
            
            // Show error state
            if (buttonElement) {
                buttonElement.disabled = false;
                buttonElement.innerHTML = '❌ Error';
                setTimeout(() => {
                    buttonElement.innerHTML = '🔊 Read Aloud';
                }, 2000);
            }
        }
    }

    /**
     * Stop currently playing audio
     */
    stop() {
        if (this.audio) {
            this.audio.pause();
            this.audio.currentTime = 0;
        }
        this.currentlyPlaying = null;
    }
}

// Create global voice player instance
const voicePlayer = new VoiceHintPlayer();

/**
 * Function to add voice buttons to existing hints
 * Call this after your hints are loaded on the page
 */
function addVoiceButtonsToHints() {
    // Find all hint elements (adjust selector based on your HTML structure)
    const hintElements = document.querySelectorAll('.hint-item, .hint-text, [data-hint-text]');
    
    hintElements.forEach((hintElement, index) => {
        // Check if voice button already exists
        if (hintElement.querySelector('.voice-button')) {
            return; // Skip if already added
        }

        // Get hint text
        const hintText = hintElement.textContent || hintElement.getAttribute('data-hint-text');
        
        if (!hintText || hintText.trim().length === 0) {
            return; // Skip empty hints
        }

        // Create voice button
        const voiceButton = document.createElement('button');
        voiceButton.className = 'voice-button';
        voiceButton.innerHTML = '🔊 Read Aloud';
        voiceButton.style.cssText = `
            margin-left: 8px;
            padding: 4px 8px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            transition: background 0.2s;
        `;

        // Add hover effect
        voiceButton.addEventListener('mouseenter', () => {
            voiceButton.style.background = '#45a049';
        });

        voiceButton.addEventListener('mouseleave', () => {
            voiceButton.style.background = '#4CAF50';
        });

        // Add click handler
        voiceButton.addEventListener('click', () => {
            voicePlayer.playHint(hintText, 'hints', voiceButton);
        });

        // Add button to hint element
        hintElement.appendChild(voiceButton);
    });
}

/**
 * Example: How to integrate with your existing hint loading
 */
// If you have a function that loads hints, modify it like this:

/*
async function loadHints(sessionId) {
    try {
        const response = await fetch(`/free-journal/${sessionId}/hints`);
        const hints = await response.json();
        
        // Display hints in your UI
        displayHints(hints);
        
        // Add voice buttons to the newly displayed hints
        setTimeout(() => {
            addVoiceButtonsToHints();
        }, 100);
        
    } catch (error) {
        console.error('Error loading hints:', error);
    }
}
*/

/**
 * Example: How to add voice button to a single hint
 */
function addVoiceButtonToHint(hintElement, hintText) {
    // Remove existing voice button if any
    const existingButton = hintElement.querySelector('.voice-button');
    if (existingButton) {
        existingButton.remove();
    }

    // Create new voice button
    const voiceButton = document.createElement('button');
    voiceButton.className = 'voice-button';
    voiceButton.innerHTML = '🔊 Read Aloud';
    voiceButton.style.cssText = `
        margin-left: 8px;
        padding: 4px 8px;
        background: #4CAF50;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
        transition: background 0.2s;
    `;

    voiceButton.addEventListener('click', () => {
        voicePlayer.playHint(hintText, 'hints', voiceButton);
    });

    hintElement.appendChild(voiceButton);
}

/**
 * CSS styles for voice buttons (add to your CSS file)
 */
const voiceButtonStyles = `
.voice-button {
    margin-left: 8px;
    padding: 4px 8px;
    background: #4CAF50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    transition: all 0.2s ease;
    opacity: 0.8;
}

.voice-button:hover {
    background: #45a049;
    opacity: 1;
    transform: translateY(-1px);
}

.voice-button:disabled {
    background: #cccccc;
    cursor: not-allowed;
    opacity: 0.6;
}

.voice-button.playing {
    background: #2196F3;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.7; }
    100% { opacity: 1; }
}
`;

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { VoiceHintPlayer, addVoiceButtonsToHints, voiceButtonStyles };
}