/**
 * Silence Detector - Pure domain logic for detecting silence after speech
 *
 * Tracks when speech starts and ends, and determines if silence has exceeded
 * a configurable threshold (e.g., 3 seconds).
 *
 * This is a pure domain model with no browser API dependencies.
 */

import { getSilenceThreshold } from './config.js';

export class SilenceDetector {
    /**
     * Create a SilenceDetector instance
     * @param {Object} options - Configuration options
     * @param {number} options.silenceThreshold - Silence threshold in milliseconds (optional, if not provided uses runtime config)
     */
    constructor(options = {}) {
        // Store the explicit threshold if provided, otherwise null (will use runtime config)
        this.explicitThreshold = options.silenceThreshold ?? null;
        this.lastSpeechTime = null;
        this.speechActive = false;
    }

    /**
     * Get the current silence threshold
     * Uses explicit threshold if provided, otherwise gets from runtime config
     * @returns {number} Silence threshold in milliseconds
     */
    getSilenceThreshold() {
        return this.explicitThreshold ?? getSilenceThreshold();
    }

    /**
     * Record when speech starts
     * @param {number} timestamp - Timestamp when speech started (optional, defaults to Date.now())
     */
    onSpeechStart(timestamp = Date.now()) {
        this.lastSpeechTime = timestamp;
        this.speechActive = true;
    }

    /**
     * Record when speech ends
     * @param {number} timestamp - Timestamp when speech ended (optional, defaults to Date.now())
     */
    onSpeechEnd(timestamp = Date.now()) {
        this.lastSpeechTime = timestamp;
        this.speechActive = false;
    }

    /**
     * Check if silence threshold has been exceeded
     * @param {number} currentTime - Current timestamp (optional, defaults to Date.now())
     * @returns {boolean} True if silence has exceeded threshold
     */
    isSilent(currentTime = Date.now()) {
        // If no speech has occurred yet, not silent
        if (this.lastSpeechTime === null) {
            return false;
        }

        // If speech is currently active, not silent
        if (this.speechActive) {
            return false;
        }

        // Calculate elapsed time since last speech
        const elapsed = currentTime - this.lastSpeechTime;

        // Check if silence threshold exceeded (use dynamic threshold)
        return elapsed >= this.getSilenceThreshold();
    }

    /**
     * Get the duration of silence since last speech
     * @param {number} currentTime - Current timestamp (optional, defaults to Date.now())
     * @returns {number} Duration of silence in milliseconds, or 0 if speech is active
     */
    getSilenceDuration(currentTime = Date.now()) {
        if (this.lastSpeechTime === null || this.speechActive) {
            return 0;
        }

        const duration = currentTime - this.lastSpeechTime;
        // Return 0 for negative durations (defensive programming)
        return Math.max(0, duration);
    }

    /**
     * Reset the silence detector to initial state
     */
    reset() {
        this.lastSpeechTime = null;
        this.speechActive = false;
    }
}
