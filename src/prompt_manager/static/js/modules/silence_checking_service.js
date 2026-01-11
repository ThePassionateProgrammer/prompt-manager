/**
 * Silence Checking Service
 *
 * Manages interval-based checking for silence detection and auto-pause.
 * Encapsulates the complexity of:
 * - Starting/stopping silence checking intervals
 * - Coordinating with conversation mode state
 * - Detecting both normal silence (auto-send) and extended silence (auto-pause)
 *
 * This service follows the Single Responsibility Principle by handling
 * only the timing and coordination aspects, delegating silence detection
 * to SilenceDetector and state management to ConversationMode.
 */

import { HANDS_FREE_CONFIG } from './config.js';

export class SilenceCheckingService {
    /**
     * Create a SilenceCheckingService instance
     * @param {Object} silenceDetector - The silence detector instance
     * @param {Object} conversationMode - The conversation mode state machine
     * @param {Object} options - Configuration options
     * @param {number} options.checkInterval - How often to check (ms)
     * @param {number} options.extendedSilenceThreshold - Extended silence threshold (ms)
     */
    constructor(silenceDetector, conversationMode, options = {}) {
        this.silenceDetector = silenceDetector;
        this.conversationMode = conversationMode;
        this.interval = null;

        // Configuration - use config defaults if not provided
        this.CHECK_INTERVAL_MS = options.checkInterval || HANDS_FREE_CONFIG.SILENCE_CHECK_INTERVAL_MS;
        this.EXTENDED_SILENCE_MS = options.extendedSilenceThreshold || HANDS_FREE_CONFIG.EXTENDED_SILENCE_THRESHOLD_MS;
    }

    /**
     * Start checking for silence
     * @param {Function} onSilenceDetected - Callback when normal silence threshold exceeded
     * @param {Function} onExtendedSilence - Callback when extended silence threshold exceeded
     */
    start(onSilenceDetected, onExtendedSilence) {
        // Don't start multiple intervals
        if (this.interval) {
            return;
        }

        this.interval = setInterval(() => {
            // Check if still in LISTENING state
            if (this.conversationMode.state !== 'LISTENING') {
                console.log('[SilenceCheckingService] State changed from LISTENING - stopping');
                this.stop();
                return;
            }

            const silenceDuration = this.silenceDetector.getSilenceDuration();

            // Check for extended silence (10+ seconds) - auto-pause
            if (silenceDuration !== null && silenceDuration > this.EXTENDED_SILENCE_MS) {
                console.log(`[SilenceCheckingService] Extended silence (${silenceDuration}ms) - auto-pausing`);
                this.stop();
                if (onExtendedSilence) {
                    onExtendedSilence();
                }
                return;
            }

            // Check for normal silence - auto-send
            if (this.silenceDetector.isSilent()) {
                console.log('[SilenceCheckingService] Silence threshold exceeded - triggering auto-send');
                this.stop();
                if (onSilenceDetected) {
                    onSilenceDetected();
                }
                return;
            }
        }, this.CHECK_INTERVAL_MS);
    }

    /**
     * Stop checking for silence
     */
    stop() {
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
    }

    /**
     * Check if silence checking is currently running
     * @returns {boolean} True if checking is active
     */
    isRunning() {
        return this.interval !== null;
    }
}
