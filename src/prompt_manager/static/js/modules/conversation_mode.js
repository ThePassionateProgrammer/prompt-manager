/**
 * Conversation Mode Module
 *
 * Manages the conversation mode state machine and UI interactions.
 * Implements the State Pattern for voice conversation flow.
 *
 * Two Modes:
 * - Manual Mode: IDLE → LISTENING (immediate transcription)
 * - Hands-Free Mode: IDLE → WAKE_LISTENING (waits for wake word)
 *
 * State Transitions (Manual Mode):
 * - IDLE → LISTENING (activate)
 * - LISTENING → PAUSED (pause)
 * - LISTENING → SENDING (send message)
 * - PAUSED → LISTENING (resume)
 * - SENDING → PLAYING (receive response)
 * - PLAYING → LISTENING (finish playback)
 * - ANY → IDLE (deactivate)
 *
 * State Transitions (Hands-Free Mode):
 * - IDLE → WAKE_LISTENING (activate with hands-free enabled)
 * - WAKE_LISTENING → LISTENING (wake word detected: "Hey Amber")
 * - LISTENING → WAKE_LISTENING (sleep word detected: "Sleep Amber")
 * - LISTENING → SENDING (10 seconds of silence triggers auto-send)
 * - SENDING → PLAYING (receive response)
 * - PLAYING → LISTENING (finish playback, ready for next question)
 * - ANY → IDLE (deactivate)
 *
 * Dependencies:
 * - VoiceInteraction module for controlling mic/speech
 * - showNotification function from main dashboard
 * - StateIndicator for visual state feedback
 */

import { WakeWordDetector } from './wake_word_detector.js';
import { SilenceDetector } from './silence_detector.js';

// Detector instances for hands-free mode
const wakeWordDetector = new WakeWordDetector();
const silenceDetector = new SilenceDetector();

/**
 * Helper to update state and notify state indicator.
 */
function updateState(newState) {
    conversationMode.state = newState;
    if (StateIndicator && StateIndicator.updateState) {
        StateIndicator.updateState(newState);
    }
}

// Conversation mode state machine (JavaScript implementation of domain model)
const conversationMode = {
    state: 'IDLE',
    isActive: false,
    handsFreeModeEnabled: false,

    enableHandsFreeMode() {
        this.handsFreeModeEnabled = true;
    },

    disableHandsFreeMode() {
        this.handsFreeModeEnabled = false;
    },

    onWakeWordDetected() {
        if (this.state === 'WAKE_LISTENING') {
            updateState('LISTENING');
        } else {
            console.warn('Wake word detected but not in WAKE_LISTENING state');
        }
    },

    onSleepWordDetected() {
        if (!this.handsFreeModeEnabled) {
            return;
        }
        if (this.state === 'LISTENING') {
            updateState('WAKE_LISTENING');
        } else {
            console.warn('Sleep word detected but not in LISTENING state');
        }
    },

    onSilenceDetected() {
        if (!this.handsFreeModeEnabled) {
            return;
        }
        if (this.state === 'LISTENING') {
            updateState('SENDING');
        }
    },

    activate() {
        if (this.isActive) throw new Error('Already active');
        this.isActive = true;
        if (this.handsFreeModeEnabled) {
            updateState('WAKE_LISTENING');
        } else {
            updateState('LISTENING');
        }
    },

    deactivate() {
        this.isActive = false;
        updateState('IDLE');
    },

    sendMessage() {
        if (!this.isActive) throw new Error('Not active');
        if (this.state === 'SENDING') throw new Error('Already sending');
        if (this.state === 'PLAYING') throw new Error('Cannot send while playing');
        if (this.state === 'LISTENING' || this.state === 'PAUSED') {
            updateState('SENDING');
        }
    },

    receiveResponse() {
        if (this.state !== 'SENDING') throw new Error('Not waiting for response');
        updateState('PLAYING');
    },

    finishPlayback() {
        if (this.state !== 'PLAYING') throw new Error('Not playing');
        updateState('LISTENING');
    },

    pauseListening() {
        if (this.state !== 'LISTENING') throw new Error('Cannot pause');
        updateState('PAUSED');
    },

    resumeListening() {
        if (this.state !== 'PAUSED') throw new Error('Not paused');
        updateState('LISTENING');
    },

    interruptPlayback() {
        if (this.state !== 'PLAYING') throw new Error('Not playing');
        updateState('LISTENING');
    },

    shouldBeListening() {
        return this.state === 'LISTENING' || this.state === 'WAKE_LISTENING';
    },

    shouldAutoPlay() {
        return this.isActive && this.state === 'SENDING';
    },

    shouldAutoRestart() {
        return this.isActive && this.state === 'PLAYING';
    }
};

// Dependencies injected from main dashboard
let VoiceInteraction = null;
let showNotification = null;
let StateIndicator = null;

/**
 * Initialize dependencies from main dashboard.
 * Must be called before using UI functions.
 */
export function initializeDependencies(deps) {
    VoiceInteraction = deps.VoiceInteraction;
    showNotification = deps.showNotification;
    StateIndicator = deps.StateIndicator;
}

/**
 * Toggle conversation mode on/off.
 */
export function toggleConversationMode() {
    if (conversationMode.isActive) {
        deactivateConversationMode();
    } else {
        activateConversationMode();
    }
}

/**
 * Activate conversation mode.
 * Starts auto-listening and enables hands-free loop.
 */
export function activateConversationMode() {
    try {
        conversationMode.activate();

        // Update button UI
        const btn = document.getElementById('conversation-mode-btn');
        btn.classList.add('active');

        // Keep mic button enabled for pause/resume functionality
        const voiceBtn = document.getElementById('voice-btn');
        voiceBtn.title = 'Pause/Resume Listening';

        // Auto-start listening
        VoiceInteraction.startListening();

        showNotification('Conversation Mode activated - speak naturally!', 'success');
    } catch (error) {
        console.error('Failed to activate conversation mode:', error);
        showNotification('Failed to activate conversation mode', 'error');
    }
}

/**
 * Deactivate conversation mode.
 * Stops listening/speaking and returns to manual mode.
 */
export function deactivateConversationMode() {
    conversationMode.deactivate();

    // Update button UI
    const btn = document.getElementById('conversation-mode-btn');
    btn.classList.remove('active');

    // Restore mic button title
    const voiceBtn = document.getElementById('voice-btn');
    voiceBtn.title = 'Voice Input';

    // Stop any active listening or speaking
    if (VoiceInteraction.getIsListening()) {
        VoiceInteraction.stopListening();
    }
    if (VoiceInteraction.getIsSpeaking()) {
        VoiceInteraction.cancelSpeech();
    }

    showNotification('Conversation Mode deactivated', 'info');
}

/**
 * Get the conversation mode state machine.
 * Used for dependency injection into other modules.
 *
 * @returns {Object} The conversation mode state machine
 */
export function getConversationMode() {
    return conversationMode;
}

/**
 * Get the wake word detector instance.
 * Used by voice_interaction for transcript processing.
 *
 * @returns {WakeWordDetector} The wake word detector instance
 */
export function getWakeWordDetector() {
    return wakeWordDetector;
}

/**
 * Get the silence detector instance.
 * Used by voice_interaction for silence checking.
 *
 * @returns {SilenceDetector} The silence detector instance
 */
export function getSilenceDetector() {
    return silenceDetector;
}

/**
 * Enable hands-free mode.
 * When enabled, conversation mode starts in WAKE_LISTENING state.
 */
export function enableHandsFreeMode() {
    conversationMode.enableHandsFreeMode();
    console.log('[ConversationMode] Hands-free mode enabled');
}

/**
 * Disable hands-free mode.
 * When disabled, conversation mode starts in LISTENING state.
 */
export function disableHandsFreeMode() {
    conversationMode.disableHandsFreeMode();
    console.log('[ConversationMode] Hands-free mode disabled');
}
