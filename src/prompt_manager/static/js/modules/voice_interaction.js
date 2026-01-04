/**
 * Voice Interaction Module
 *
 * Manages voice input (speech-to-text) and voice output (text-to-speech)
 * using Browser Web Speech API.
 *
 * Dependencies:
 * - Browser must support webkitSpeechRecognition and speechSynthesis
 * - Requires conversationMode object from main dashboard
 * - Requires isLoading state from main dashboard
 * - Requires showNotification function from main dashboard
 */

// Voice interaction state
let voiceRecognition = null;
let voiceSynthesis = window.speechSynthesis;
let isListening = false;
let isSpeaking = false;
let processedResultIndex = 0;

// Dependencies injected from main dashboard
let conversationMode = null;
let getIsLoading = null;
let showNotification = null;

/**
 * Initialize dependencies from main dashboard.
 * Must be called before using any other functions.
 */
export function initializeDependencies(deps) {
    conversationMode = deps.conversationMode;
    getIsLoading = deps.getIsLoading;
    showNotification = deps.showNotification;
}

/**
 * Initialize Web Speech API for voice recognition.
 * Sets up event handlers for voice input.
 */
export function initializeVoiceRecognition() {
    // Check if browser supports Web Speech API
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        console.warn('Speech recognition not supported in this browser');
        const voiceBtn = document.getElementById('voice-btn');
        if (voiceBtn) {
            voiceBtn.disabled = true;
            voiceBtn.title = 'Voice input not supported in this browser';
            voiceBtn.style.opacity = '0.3';
        }
        return;
    }

    voiceRecognition = new SpeechRecognition();
    voiceRecognition.continuous = false;
    voiceRecognition.interimResults = false;
    voiceRecognition.lang = 'en-US';

    voiceRecognition.onresult = function(event) {
        const chatInput = document.getElementById('chat-input');

        // Process only NEW results (not previously processed ones)
        // In continuous mode, event.results accumulates all results from the session
        for (let i = processedResultIndex; i < event.results.length; i++) {
            const result = event.results[i];

            // Only process final results to avoid duplicates
            if (result.isFinal) {
                const transcript = result[0].transcript;

                // Append transcript to existing text or set as new text
                if (chatInput.value.trim()) {
                    chatInput.value += ' ' + transcript;
                } else {
                    chatInput.value = transcript;
                }

                processedResultIndex = i + 1;
            }
        }

        // Trigger input event to resize textarea
        chatInput.dispatchEvent(new Event('input'));
        chatInput.focus();
    };

    voiceRecognition.onerror = function(event) {
        console.error('Speech recognition error:', event.error);
        stopListening();

        if (event.error === 'no-speech') {
            showNotification('No speech detected. Please try again.', 'warning');
        } else if (event.error === 'not-allowed') {
            showNotification('Microphone access denied. Please enable microphone permissions.', 'error');
        } else {
            showNotification(`Voice input error: ${event.error}`, 'error');
        }
    };

    voiceRecognition.onend = function() {
        // In conversation mode, don't auto-stop - let user control with mic/send buttons
        if (!conversationMode.isActive) {
            stopListening();
        } else {
            // Voice recognition stopped unexpectedly in conversation mode - restart it
            if (conversationMode.shouldBeListening() && !getIsLoading()) {
                console.log('Voice recognition ended unexpectedly, restarting...');
                // Small delay before restarting
                setTimeout(() => {
                    if (conversationMode.shouldBeListening() && !getIsLoading()) {
                        try {
                            voiceRecognition.start();
                        } catch (e) {
                            console.error('Failed to restart voice recognition:', e);
                        }
                    }
                }, 300);
            }
        }
    };
}

/**
 * Toggle voice input on/off.
 * In conversation mode, pauses/resumes listening.
 * In manual mode, starts/stops listening.
 */
export function toggleVoiceInput() {
    // In conversation mode, mic button pauses/resumes listening
    if (conversationMode.isActive) {
        if (isListening) {
            conversationMode.pauseListening();
            stopListening();
        } else if (conversationMode.state === 'PAUSED') {
            conversationMode.resumeListening();
            startListening();
        }
    } else {
        // Manual mode
        if (isListening) {
            stopListening();
        } else {
            startListening();
        }
    }
}

/**
 * Start listening for speech input.
 * Uses continuous mode when in conversation mode.
 */
export function startListening() {
    if (!voiceRecognition) {
        showNotification('Voice recognition not available', 'error');
        return;
    }

    if (isListening) {
        return;
    }

    try {
        // Use continuous mode in conversation mode
        voiceRecognition.continuous = conversationMode.isActive;

        // Reset processed result index for new session
        processedResultIndex = 0;

        isListening = true;
        voiceRecognition.start();

        const voiceBtn = document.getElementById('voice-btn');
        voiceBtn.classList.add('listening');
        voiceBtn.title = 'Listening... Click to stop';

        if (!conversationMode.isActive) {
            showNotification('Listening...', 'info');
        }
    } catch (error) {
        console.error('Failed to start voice recognition:', error);
        isListening = false;
        showNotification('Failed to start voice input', 'error');
    }
}

/**
 * Stop listening for speech input.
 */
export function stopListening() {
    if (!isListening) {
        return;
    }

    isListening = false;

    if (voiceRecognition) {
        try {
            voiceRecognition.stop();
        } catch (error) {
            console.error('Error stopping voice recognition:', error);
        }
    }

    const voiceBtn = document.getElementById('voice-btn');
    voiceBtn.classList.remove('listening');
    voiceBtn.title = 'Voice Input';
}

/**
 * Speak text using text-to-speech.
 * Can be stopped by calling again (toggle behavior).
 *
 * @param {string} text - Text to speak
 * @param {HTMLElement} button - Play button element (optional)
 */
export function speakText(text, button) {
    if (!voiceSynthesis) {
        showNotification('Text-to-speech not supported in this browser', 'error');
        return;
    }

    // Stop if already speaking
    if (isSpeaking) {
        stopSpeaking(button);
        return;
    }

    // Cancel any ongoing speech
    voiceSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    utterance.lang = 'en-US';

    utterance.onstart = function() {
        isSpeaking = true;
        if (button) {
            button.classList.add('speaking');
            button.innerHTML = '⏸️ Stop';
        }
    };

    utterance.onend = function() {
        isSpeaking = false;
        if (button) {
            button.classList.remove('speaking');
            button.innerHTML = '▶️ Play';
        }
    };

    utterance.onerror = function(event) {
        console.error('Speech synthesis error:', event);
        isSpeaking = false;
        if (button) {
            button.classList.remove('speaking');
            button.innerHTML = '▶️ Play';
        }
        showNotification('Text-to-speech error', 'error');
    };

    voiceSynthesis.speak(utterance);
}

/**
 * Stop speaking.
 *
 * @param {HTMLElement} button - Play button element (optional)
 */
export function stopSpeaking(button) {
    if (voiceSynthesis) {
        voiceSynthesis.cancel();
    }

    isSpeaking = false;

    if (button) {
        button.classList.remove('speaking');
        button.innerHTML = '▶️ Play';
    }
}

/**
 * Play message text from a message div.
 * Extracts text from message and speaks it.
 *
 * @param {HTMLElement} button - Play button that was clicked
 */
export function playMessage(button) {
    // Get the message text from the message div
    const messageDiv = button.closest('.message');
    const messageText = messageDiv.querySelector('.message-text').textContent;

    speakText(messageText, button);
}

/**
 * Auto-play response in conversation mode.
 * Automatically restarts listening after playback finishes.
 *
 * @param {string} text - Response text to speak
 */
export function autoPlayResponse(text) {
    // Auto-play response in conversation mode
    if (!voiceSynthesis) {
        console.error('Text-to-speech not supported');
        // Still auto-restart listening even if TTS fails
        if (conversationMode.shouldAutoRestart()) {
            conversationMode.finishPlayback();
            startListening();
        }
        return;
    }

    // Cancel any ongoing speech
    voiceSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    utterance.lang = 'en-US';

    utterance.onstart = function() {
        isSpeaking = true;
    };

    utterance.onend = function() {
        isSpeaking = false;

        // Auto-restart listening after playback finishes
        if (conversationMode.shouldAutoRestart()) {
            conversationMode.finishPlayback();
            // Longer delay before restarting to prevent immediate re-trigger
            setTimeout(() => {
                if (conversationMode.shouldBeListening() && !getIsLoading()) {
                    startListening();
                }
            }, 1000);
        }
    };

    utterance.onerror = function(event) {
        console.error('Speech synthesis error:', event);
        isSpeaking = false;

        // Still auto-restart listening even if playback fails
        if (conversationMode.shouldAutoRestart()) {
            conversationMode.finishPlayback();
            startListening();
        }
    };

    voiceSynthesis.speak(utterance);
}

/**
 * Get current listening state.
 *
 * @returns {boolean} True if currently listening
 */
export function getIsListening() {
    return isListening;
}

/**
 * Get current speaking state.
 *
 * @returns {boolean} True if currently speaking
 */
export function getIsSpeaking() {
    return isSpeaking;
}

/**
 * Cancel any ongoing speech synthesis.
 * Used when deactivating conversation mode.
 */
export function cancelSpeech() {
    if (voiceSynthesis) {
        voiceSynthesis.cancel();
    }
    isSpeaking = false;
}
