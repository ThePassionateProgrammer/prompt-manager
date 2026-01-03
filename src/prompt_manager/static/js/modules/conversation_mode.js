/**
 * Conversation Mode Module
 *
 * Manages the conversation mode state machine and UI interactions.
 * Implements the State Pattern as defined in the domain model.
 *
 * State Transitions:
 * - IDLE → LISTENING (activate)
 * - LISTENING → PAUSED (pause)
 * - LISTENING → SENDING (send message)
 * - PAUSED → LISTENING (resume)
 * - PAUSED → SENDING (send message)
 * - SENDING → PLAYING (receive response)
 * - PLAYING → LISTENING (finish playback / auto-restart)
 * - ANY → IDLE (deactivate)
 *
 * Dependencies:
 * - VoiceInteraction module for controlling mic/speech
 * - showNotification function from main dashboard
 */

// Conversation mode state machine (JavaScript implementation of domain model)
const conversationMode = {
    state: 'IDLE',
    isActive: false,

    activate() {
        if (this.isActive) throw new Error('Already active');
        this.isActive = true;
        this.state = 'LISTENING';
    },

    deactivate() {
        this.isActive = false;
        this.state = 'IDLE';
    },

    sendMessage() {
        if (!this.isActive) throw new Error('Not active');
        if (this.state === 'SENDING') throw new Error('Already sending');
        if (this.state === 'PLAYING') throw new Error('Cannot send while playing');
        if (this.state === 'LISTENING' || this.state === 'PAUSED') {
            this.state = 'SENDING';
        }
    },

    receiveResponse() {
        if (this.state !== 'SENDING') throw new Error('Not waiting for response');
        this.state = 'PLAYING';
    },

    finishPlayback() {
        if (this.state !== 'PLAYING') throw new Error('Not playing');
        this.state = 'LISTENING';
    },

    pauseListening() {
        if (this.state !== 'LISTENING') throw new Error('Cannot pause');
        this.state = 'PAUSED';
    },

    resumeListening() {
        if (this.state !== 'PAUSED') throw new Error('Not paused');
        this.state = 'LISTENING';
    },

    interruptPlayback() {
        if (this.state !== 'PLAYING') throw new Error('Not playing');
        this.state = 'LISTENING';
    },

    shouldBeListening() {
        return this.state === 'LISTENING';
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

/**
 * Initialize dependencies from main dashboard.
 * Must be called before using UI functions.
 */
export function initializeDependencies(deps) {
    VoiceInteraction = deps.VoiceInteraction;
    showNotification = deps.showNotification;
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

        // Disable standalone mic button (conversation mode controls mic)
        const voiceBtn = document.getElementById('voice-btn');
        voiceBtn.disabled = true;
        voiceBtn.style.opacity = '0.5';

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

    // Re-enable standalone mic button
    const voiceBtn = document.getElementById('voice-btn');
    voiceBtn.disabled = false;
    voiceBtn.style.opacity = '1';

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
