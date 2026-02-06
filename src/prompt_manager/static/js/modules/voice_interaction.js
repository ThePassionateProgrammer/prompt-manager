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
import { CommandDetector } from './command_detector.js';
import { TranscriptProcessor } from './transcript_processor.js';
import { SilenceCheckingService } from './silence_checking_service.js';
import * as VoiceSettings from './voice_settings.js';
import * as IncrementalSpeech from './incremental_speech.js';

// Voice interaction state
let voiceRecognition = null;
let voiceSynthesis = window.speechSynthesis;
let isListening = false;
let isSpeaking = false;
let processedResultIndex = 0;
let lastAIResponse = null;  // Store last AI response for "repeat that" command

// Dependencies injected from main dashboard
let conversationMode = null;
let conversationModeModule = null;
let getIsLoading = null;
let showNotification = null;

// Voice command detector for pause/resume commands
const voiceCommandDetector = new VoiceCommandDetector();

// Command detector for Ember command word system ("Ember, repeat that")
const commandDetector = new CommandDetector();

// Transcript processor (created after dependencies initialized)
let transcriptProcessor = null;

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

    // Initialize transcript processor
    const wakeWordDetector = conversationModeModule?.getWakeWordDetector?.();
    transcriptProcessor = new TranscriptProcessor({
        wakeWordDetector,
        voiceCommandDetector,
        commandDetector,
        conversationMode
    });

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
    voiceRecognition.interimResults = true;  // Enable interim results to detect ongoing speech

    // Apply user's STT settings
    VoiceSettings.applySTTSettings(voiceRecognition);

    voiceRecognition.onresult = function(event) {
        const chatInput = document.getElementById('chat-input');

        // BARGE-IN: If AI is speaking and user speaks, interrupt the AI
        if (conversationMode && conversationMode.isActive && conversationMode.state === 'PLAYING') {
            console.log('[Voice] Barge-in detected - interrupting AI speech');
            // Stop the AI speech
            IncrementalSpeech.stop();
            voiceSynthesis.cancel();
            isSpeaking = false;
            // Transition to LISTENING state
            try {
                conversationMode.interruptPlayback();
                showNotification('Interrupted - listening...', 'info');
            } catch (e) {
                console.error('Failed to interrupt playback:', e);
            }
        }

        // In hands-free mode, ANY result (interim or final) indicates ongoing speech
        // Reset the silence timer to prevent premature auto-send
        if (conversationMode && conversationMode.handsFreeModeEnabled) {
            const silenceDetector = conversationModeModule?.getSilenceDetector?.();
            if (silenceDetector) {
                // Mark speech as active - this resets the silence countdown
                silenceDetector.onSpeechStart(Date.now());
            }
        }

        // Process only NEW results (not previously processed ones)
        // In continuous mode, event.results accumulates all results from the session
        for (let i = processedResultIndex; i < event.results.length; i++) {
            const result = event.results[i];

            // Only process final results to avoid duplicates
            if (result.isFinal) {
                const transcript = result[0].transcript;

                // In hands-free mode, stop any existing silence checking when new speech arrives
                // We'll restart it after processing if this is a TRANSCRIBE action
                if (conversationMode && conversationMode.handsFreeModeEnabled && silenceCheckingService) {
                    silenceCheckingService.stop();
                }

                // Process transcript using TranscriptProcessor
                if (transcriptProcessor) {
                    console.log('[Hands-free] Processing transcript:', transcript);
                    console.log('[Hands-free] State:', conversationMode?.state);

                    const processingResult = transcriptProcessor.process(transcript);
                    console.log('[Hands-free] Processing result:', processingResult);

                    // Handle the action based on processing result
                    switch (processingResult.action) {
                        case 'WAKE':
                            console.log('[Hands-free] Wake word detected - starting transcription');
                            conversationMode.onWakeWordDetected();
                            if (processingResult.message) {
                                showNotification(processingResult.message, 'success');
                            }
                            processedResultIndex = i + 1;
                            continue;

                        case 'SLEEP':
                            console.log('[Hands-free] Sleep word detected - stopping transcription');
                            conversationMode.onSleepWordDetected();
                            if (processingResult.message) {
                                showNotification(processingResult.message, 'info');
                            }
                            processedResultIndex = i + 1;
                            continue;

                        case 'PAUSE':
                            console.log('[Hands-free] Pause command detected');
                            conversationMode.pauseListening();
                            if (processingResult.message) {
                                showNotification(processingResult.message, 'info');
                            }
                            processedResultIndex = i + 1;
                            continue;

                        case 'RESUME':
                            console.log('[Hands-free] Resume command detected');
                            conversationMode.resumeListening();
                            if (processingResult.message) {
                                showNotification(processingResult.message, 'success');
                            }
                            processedResultIndex = i + 1;
                            continue;

                        case 'REPEAT':
                            console.log('[Hands-free] Repeat command detected');
                            if (lastAIResponse) {
                                speakText(lastAIResponse);
                                showNotification('Repeating last response...', 'info');
                            } else {
                                showNotification('No previous response to repeat', 'warning');
                            }
                            processedResultIndex = i + 1;
                            continue;

                        case 'TRANSCRIBE_MODE':
                            console.log('[Hands-free] Transcribe command detected');
                            if (processingResult.message) {
                                showNotification(processingResult.message, 'info');
                            }
                            processedResultIndex = i + 1;
                            continue;

                        case 'IGNORE':
                            console.log('[Hands-free] In standby/paused mode - not transcribing');
                            processedResultIndex = i + 1;
                            continue;

                        case 'TRANSCRIBE':
                            // Fall through to add transcript to chat input
                            break;
                    }
                }

                // Append transcript to existing text or set as new text
                if (chatInput.value.trim()) {
                    chatInput.value += ' ' + transcript;
                } else {
                    chatInput.value = transcript;
                }

                // Start silence checking for TRANSCRIBE actions (text added to input)
                // Mark speech as ended - countdown starts from this moment
                // If interim results arrive, onSpeechStart will be called above,
                // which prevents isSilent() from returning true
                if (conversationMode && conversationMode.handsFreeModeEnabled) {
                    const silenceDetector = conversationModeModule?.getSilenceDetector?.();
                    if (silenceDetector) {
                        silenceDetector.onSpeechEnd(Date.now());
                        startSilenceChecking();
                    }
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
        // Note: Silence checking is started in onresult after each final transcript.
        // This gives accurate 5-second timing from when user actually stopped speaking,
        // not from when Chrome's recognition session ends (~10s later).

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

    // Define callback for silence detection (triggers auto-send)
    const onSilenceDetected = () => {
        console.log('[Hands-free] Silence threshold exceeded - auto-sending message...');
        const chatInput = document.getElementById('chat-input');
        if (chatInput && chatInput.value.trim()) {
            console.log('[Hands-free] Message content:', chatInput.value.trim());
            // Just click send button - sendMessage() handles state transition
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

    // Start the silence checking service
    silenceCheckingService.start(onSilenceDetected);
}

/**
 * Stop silence checking interval (for hands-free mode cleanup)
 */
export function stopSilenceChecking() {
    if (silenceCheckingService) {
        silenceCheckingService.stop();
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
        // Can only pause from LISTENING state (not WAKE_LISTENING - need to say sleep word)
        if (isListening && conversationMode.state === 'LISTENING') {
            conversationMode.pauseListening();
            stopListening();
        } else if (conversationMode.state === 'PAUSED') {
            conversationMode.resumeListening();
            startListening();
        } else if (conversationMode.state === 'WAKE_LISTENING') {
            // In hands-free WAKE_LISTENING state, mic click has no effect
            // User should say sleep word to exit hands-free mode
            console.log('[Hands-free] In WAKE_LISTENING state - say sleep word to exit');
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
    console.log('[Voice] startListening called, isListening:', isListening);
    if (!voiceRecognition) {
        showNotification('Voice recognition not available', 'error');
        return;
    }

    if (isListening) {
        console.log('[Voice] startListening called but already listening, skipping');
        return;
    }

    try {
        // Use continuous mode in conversation mode
        voiceRecognition.continuous = conversationMode.isActive;

        // Reset processed result index for new session
        processedResultIndex = 0;

        isListening = true;
        console.log('[Voice] Starting listening, state:', conversationMode?.state);
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
    console.log('[Voice] stopListening called, isListening:', isListening);
    if (!isListening) {
        return;
    }

    isListening = false;
    console.log('[Voice] Stopped listening');

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
 * Uses voice settings from VoiceSettings module.
 *
 * @param {string} text - Text to speak
 * @param {HTMLElement} button - Play button element (optional)
 */
export async function speakText(text, button) {
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

    // Apply user's voice settings
    await VoiceSettings.applyTTSSettings(utterance);

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
 * Uses voice settings from VoiceSettings module.
 *
 * @param {string} text - Response text to speak
 */
export async function autoPlayResponse(text) {
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

    // Apply user's voice settings
    await VoiceSettings.applyTTSSettings(utterance);

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

/**
 * Store the last AI response for "repeat that" command.
 * Should be called when a new AI response is received.
 *
 * @param {string} responseText - The AI response text to store
 */
export function storeLastResponse(responseText) {
    lastAIResponse = responseText;
    console.log('[Voice] Stored last AI response for repeat command');
}

// ============================================================
// INCREMENTAL SPEECH - Speak as text streams in
// ============================================================

/**
 * Start incremental speech for a streaming response.
 * Call this before starting to receive streaming chunks.
 *
 * @param {Function} onComplete - Optional callback when all speech finishes
 */
export function startIncrementalSpeech(onComplete) {
    IncrementalSpeech.initialize();

    // Set up completion handler for conversation mode
    if (onComplete) {
        IncrementalSpeech.setOnComplete(() => {
            isSpeaking = false;
            onComplete();
        });
    } else {
        IncrementalSpeech.setOnComplete(() => {
            isSpeaking = false;
        });
    }

    isSpeaking = true;
}

/**
 * Add a streaming chunk to the incremental speech buffer.
 * Will automatically speak complete sentences.
 *
 * @param {string} chunk - Text chunk from streaming response
 */
export function addSpeechChunk(chunk) {
    IncrementalSpeech.addChunk(chunk);
}

/**
 * Finalize incremental speech when streaming completes.
 * Speaks any remaining buffered text.
 */
export function finalizeSpeech() {
    IncrementalSpeech.finalize();
}

/**
 * Stop incremental speech and clear buffers.
 */
export function stopIncrementalSpeech() {
    IncrementalSpeech.stop();
    isSpeaking = false;
}
