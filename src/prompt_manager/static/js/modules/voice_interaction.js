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

import { VoiceCommandDetector } from './voice_command_detector.js';
import { SilenceCheckingService } from './silence_checking_service.js';

// Voice interaction state
let voiceRecognition = null;
let voiceSynthesis = window.speechSynthesis;
let isListening = false;
let isSpeaking = false;
let processedResultIndex = 0;

// Dependencies injected from main dashboard
let conversationMode = null;
let conversationModeModule = null;
let getIsLoading = null;
let showNotification = null;

// Voice command detector for pause/resume commands
const voiceCommandDetector = new VoiceCommandDetector();

// Silence checking service (created after dependencies initialized)
let silenceCheckingService = null;

/**
 * Initialize dependencies from main dashboard.
 * Must be called before using any other functions.
 */
export function initializeDependencies(deps) {
    conversationMode = deps.conversationMode;
    conversationModeModule = deps.conversationModeModule;
    getIsLoading = deps.getIsLoading;
    showNotification = deps.showNotification;

    // Initialize silence checking service
    const silenceDetector = conversationModeModule?.getSilenceDetector?.();
    if (silenceDetector) {
        silenceCheckingService = new SilenceCheckingService(silenceDetector, conversationMode);
    }
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

                // Mark speech start when we receive actual speech
                if (conversationMode && conversationMode.handsFreeModeEnabled) {
                    const silenceDetector = conversationModeModule?.getSilenceDetector?.();
                    if (silenceDetector) {
                        silenceDetector.onSpeechStart();
                        console.log('[Hands-free] Speech detected, resetting silence timer');
                    }
                }

                // In hands-free mode, check for wake/sleep/pause/resume commands
                if (conversationMode && conversationMode.handsFreeModeEnabled) {
                    console.log('[Hands-free] Mode enabled, state:', conversationMode.state);
                    console.log('[Hands-free] Transcript:', transcript);

                    // Check for wake word (when in WAKE_LISTENING/standby)
                    const wakeWordDetector = conversationModeModule?.getWakeWordDetector?.();
                    if (wakeWordDetector && conversationMode.state === 'WAKE_LISTENING') {
                        const detection = wakeWordDetector.detect(transcript);
                        console.log('[Hands-free] Wake word detection:', detection);
                        if (detection.matched && detection.type === 'wake') {
                            console.log('[Hands-free] Wake word detected - starting transcription');
                            conversationMode.onWakeWordDetected();
                            showNotification('Listening...', 'success');
                            processedResultIndex = i + 1;
                            continue; // Don't add wake word to chat input
                        }
                    }

                    // Check for sleep word (when in LISTENING state)
                    if (wakeWordDetector && conversationMode.state === 'LISTENING') {
                        const detection = wakeWordDetector.detect(transcript);
                        if (detection.matched && detection.type === 'sleep') {
                            console.log('[Hands-free] Sleep word detected - stopping transcription');
                            conversationMode.onSleepWordDetected();
                            showNotification('Standby mode. Say "Hey Amber" to wake.', 'info');
                            processedResultIndex = i + 1;
                            continue; // Don't add sleep word to chat input
                        }
                    }

                    // Check for voice commands (pause/resume)
                    const commandDetection = voiceCommandDetector.detect(transcript);
                    if (commandDetection.matched) {
                        if (commandDetection.command === 'pause' && conversationMode.state === 'LISTENING') {
                            console.log('[Hands-free] Pause command detected');
                            conversationMode.pauseListening();
                            showNotification('Paused. Say "Amber, resume" to continue.', 'info');
                            processedResultIndex = i + 1;
                            continue; // Don't add pause command to chat input
                        }

                        if (commandDetection.command === 'resume' && conversationMode.state === 'PAUSED') {
                            console.log('[Hands-free] Resume command detected');
                            conversationMode.resumeListening();
                            showNotification('Resumed listening', 'success');
                            processedResultIndex = i + 1;
                            continue; // Don't add resume command to chat input
                        }
                    }
                }

                // In WAKE_LISTENING (standby) or PAUSED state, don't add any speech to input
                if (conversationMode && (conversationMode.state === 'WAKE_LISTENING' || conversationMode.state === 'PAUSED')) {
                    console.log('[Hands-free] In standby/paused mode - not transcribing');
                    processedResultIndex = i + 1;
                    continue;
                }

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

    voiceRecognition.onstart = function() {
        console.log('[Hands-free] Voice recognition started, state:', conversationMode?.state);
        // Don't mark speech start here - voice recognition auto-restarts even when silent
        // Speech start should only be marked when we actually receive a transcript
    };

    voiceRecognition.onend = function() {
        console.log('[Hands-free] Voice recognition ended, state:', conversationMode?.state);
        // Track speech end for silence detection
        if (conversationMode && conversationMode.handsFreeModeEnabled) {
            console.log('[Hands-free] Hands-free mode enabled, tracking silence');
            const silenceDetector = conversationModeModule?.getSilenceDetector?.();
            if (silenceDetector) {
                silenceDetector.onSpeechEnd();
                console.log('[Hands-free] Speech ended, starting silence checking...');
                // Start checking for silence threshold
                startSilenceChecking();
            }
        }

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
 * Start checking for silence threshold (hands-free mode)
 */
function startSilenceChecking() {
    if (!conversationMode || !conversationMode.handsFreeModeEnabled) {
        console.log('[Hands-free] Not starting silence check - hands-free disabled');
        return;
    }

    if (!silenceCheckingService) {
        console.log('[Hands-free] No silence checking service available');
        return;
    }

    // Define callbacks for silence detection
    const onSilenceDetected = () => {
        console.log('[Hands-free] Silence detected! Auto-sending message...');
        const chatInput = document.getElementById('chat-input');
        if (chatInput && chatInput.value.trim()) {
            console.log('[Hands-free] Message content:', chatInput.value.trim());
            // Just click the send button - it will handle state transitions
            const sendBtn = document.getElementById('send-btn');
            if (sendBtn) {
                sendBtn.click();
            } else {
                console.error('[Hands-free] Send button not found!');
            }
        } else {
            console.log('[Hands-free] No message to send (empty input)');
        }
    };

    const onExtendedSilence = () => {
        console.log('[Hands-free] Extended silence (>10s) detected - auto-pausing');
        conversationMode.pauseListening();
        showNotification('Auto-paused after 10 seconds of silence. Say "Amber, resume" to continue.', 'info');
    };

    // Start the silence checking service
    silenceCheckingService.start(onSilenceDetected, onExtendedSilence);
}

/**
 * Stop silence checking interval (for hands-free mode cleanup)
 */
export function stopSilenceChecking() {
    if (silenceCheckingService) {
        silenceCheckingService.stop();
        console.log('[Hands-free] Silence checking stopped');
    }
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

    // Stop silence checking service
    if (silenceCheckingService) {
        silenceCheckingService.stop();
    }

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
