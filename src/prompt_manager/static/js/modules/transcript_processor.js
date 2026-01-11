/**
 * Transcript Processor - Pure domain logic for processing speech transcripts
 *
 * Analyzes speech recognition transcripts and determines appropriate actions
 * based on conversation state, wake words, commands, and user input.
 *
 * Returns processing result with action type and instructions for caller.
 *
 * This is a pure domain model with no browser API dependencies.
 */

export class TranscriptProcessor {
    /**
     * Create a TranscriptProcessor instance
     * @param {Object} options - Configuration options
     * @param {Object} options.wakeWordDetector - Wake word detector instance
     * @param {Object} options.voiceCommandDetector - Voice command detector (pause/resume)
     * @param {Object} options.commandDetector - Command detector (Ember commands)
     * @param {Object} options.conversationMode - Conversation mode state object
     */
    constructor(options = {}) {
        this.wakeWordDetector = options.wakeWordDetector || null;
        this.voiceCommandDetector = options.voiceCommandDetector || null;
        this.commandDetector = options.commandDetector || null;
        this.conversationMode = options.conversationMode || null;
    }

    /**
     * Process a speech transcript and determine appropriate action
     * @param {string} transcript - Speech transcript to process
     * @returns {Object} Processing result:
     *   - action: 'WAKE'|'SLEEP'|'PAUSE'|'RESUME'|'REPEAT'|'TRANSCRIBE_MODE'|'TRANSCRIBE'|'IGNORE'
     *   - shouldTranscribe: boolean - whether to add to chat input
     *   - message: string|null - notification message for user (if any)
     */
    process(transcript) {
        // If hands-free mode is disabled, just transcribe everything
        if (!this.conversationMode || !this.conversationMode.handsFreeModeEnabled) {
            return {
                action: 'TRANSCRIBE',
                shouldTranscribe: true,
                message: null
            };
        }

        const state = this.conversationMode.state;

        // Check for wake word (when in WAKE_LISTENING/standby)
        if (this.wakeWordDetector && state === 'WAKE_LISTENING') {
            const detection = this.wakeWordDetector.detect(transcript);
            if (detection.matched && detection.type === 'wake') {
                return {
                    action: 'WAKE',
                    shouldTranscribe: false,
                    message: 'Listening...'
                };
            }
        }

        // Check for sleep word (when in LISTENING state)
        if (this.wakeWordDetector && state === 'LISTENING') {
            const detection = this.wakeWordDetector.detect(transcript);
            if (detection.matched && detection.type === 'sleep') {
                return {
                    action: 'SLEEP',
                    shouldTranscribe: false,
                    message: 'Standby mode. Say "Hey Amber" to wake.'
                };
            }
        }

        // Check for voice commands (pause/resume)
        if (this.voiceCommandDetector) {
            const commandDetection = this.voiceCommandDetector.detect(transcript);
            if (commandDetection.matched) {
                if (commandDetection.command === 'pause' && state === 'LISTENING') {
                    return {
                        action: 'PAUSE',
                        shouldTranscribe: false,
                        message: 'Paused. Say "Amber, resume" to continue.'
                    };
                }

                if (commandDetection.command === 'resume' && state === 'PAUSED') {
                    return {
                        action: 'RESUME',
                        shouldTranscribe: false,
                        message: 'Resumed listening'
                    };
                }
            }
        }

        // Check for Ember command word system (e.g., "Ember, repeat that")
        if (this.commandDetector && state === 'LISTENING') {
            const emberCommandDetection = this.commandDetector.detect(transcript);
            if (emberCommandDetection.matched) {
                if (emberCommandDetection.command === 'repeat') {
                    return {
                        action: 'REPEAT',
                        shouldTranscribe: false,
                        message: null  // Handler will show appropriate message
                    };
                }

                if (emberCommandDetection.command === 'transcribe') {
                    return {
                        action: 'TRANSCRIBE_MODE',
                        shouldTranscribe: false,
                        message: 'Transcribe mode - feature coming soon'
                    };
                }
            }
        }

        // In WAKE_LISTENING (standby) or PAUSED state, don't transcribe any speech
        if (state === 'WAKE_LISTENING' || state === 'PAUSED') {
            return {
                action: 'IGNORE',
                shouldTranscribe: false,
                message: null
            };
        }

        // Default: transcribe the speech in LISTENING state
        return {
            action: 'TRANSCRIBE',
            shouldTranscribe: true,
            message: null
        };
    }
}
