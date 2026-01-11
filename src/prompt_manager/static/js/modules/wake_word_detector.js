/**
 * Wake Word Detector - Pure domain logic for detecting wake and sleep words
 *
 * Analyzes speech transcripts to identify wake words (to start conversation)
 * and sleep words (to return to listening mode).
 *
 * This is a pure domain model with no browser API dependencies.
 */

import { getWakeWord, getSleepWord, getWakeWords, getSleepWords } from './config.js';

export class WakeWordDetector {
    /**
     * Create a WakeWordDetector instance
     * @param {Object} options - Configuration options
     * @param {string|string[]} options.wakeWord - Custom wake word (optional, backward compatible)
     * @param {string|string[]} options.sleepWord - Custom sleep word (optional, backward compatible)
     * @param {string[]} options.wakeWords - Array of wake words (optional)
     * @param {string[]} options.sleepWords - Array of sleep words (optional)
     */
    constructor(options = {}) {
        // Support both old API (wakeWord) and new API (wakeWords)
        // Convert single strings to arrays for uniform handling
        if (options.wakeWords) {
            this.wakeWords = Array.isArray(options.wakeWords) ? options.wakeWords : [options.wakeWords];
        } else if (options.wakeWord) {
            this.wakeWords = [options.wakeWord];
        } else {
            // Use array from config by default
            this.wakeWords = getWakeWords();
        }

        if (options.sleepWords) {
            this.sleepWords = Array.isArray(options.sleepWords) ? options.sleepWords : [options.sleepWords];
        } else if (options.sleepWord) {
            this.sleepWords = [options.sleepWord];
        } else {
            // Use array from config by default
            this.sleepWords = getSleepWords();
        }

        // Backward compatibility: expose first word as single property
        this.wakeWord = this.wakeWords[0];
        this.sleepWord = this.sleepWords[0];
    }

    /**
     * Normalize text for comparison (lowercase, trim)
     * @param {*} text - Text to normalize
     * @returns {string} Normalized text, or empty string if invalid
     * @private
     */
    _normalize(text) {
        if (typeof text !== 'string') {
            return '';
        }
        return text.toLowerCase().trim();
    }

    /**
     * Check if transcript contains any wake word
     * @param {string} transcript - Speech transcript to analyze
     * @returns {boolean} True if any wake word is detected
     */
    detectWakeWord(transcript) {
        const normalized = this._normalize(transcript);

        if (!normalized) {
            return false;
        }

        // Check against all wake words
        return this.wakeWords.some(word => {
            const normalizedWake = this._normalize(word);
            // Exact match only (per requirements)
            return normalized === normalizedWake;
        });
    }

    /**
     * Check if transcript contains any sleep word
     * @param {string} transcript - Speech transcript to analyze
     * @returns {boolean} True if any sleep word is detected
     */
    detectSleepWord(transcript) {
        const normalized = this._normalize(transcript);

        if (!normalized) {
            return false;
        }

        // Check against all sleep words
        return this.sleepWords.some(word => {
            const normalizedSleep = this._normalize(word);
            // Exact match only (per requirements)
            return normalized === normalizedSleep;
        });
    }

    /**
     * Detect both wake and sleep words in a single call
     * @param {string} transcript - Speech transcript to analyze
     * @returns {Object} Detection result: { type: 'wake'|'sleep'|null, matched: boolean }
     */
    detect(transcript) {
        if (this.detectWakeWord(transcript)) {
            return { type: 'wake', matched: true };
        }

        if (this.detectSleepWord(transcript)) {
            return { type: 'sleep', matched: true };
        }

        return { type: null, matched: false };
    }
}
