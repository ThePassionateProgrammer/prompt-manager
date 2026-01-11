/**
 * Voice Command Detector
 *
 * Detects pause/resume voice commands in speech transcripts.
 * Follows the same pattern as WakeWordDetector but for conversation control.
 *
 * Default Commands:
 * - Pause: "amber pause", "amber, pause", "pause amber"
 * - Resume: "amber resume", "amber, resume", "resume amber"
 *
 * Commands are case-insensitive and must match exactly (not part of larger sentence).
 */

import { HANDS_FREE_CONFIG } from './config.js';

export class VoiceCommandDetector {
    /**
     * Create a VoiceCommandDetector instance
     * @param {Object} options - Configuration options
     * @param {string[]} options.pauseCommands - Array of pause command variations
     * @param {string[]} options.resumeCommands - Array of resume command variations
     */
    constructor(options = {}) {
        // Use config defaults if not provided
        this.pauseCommands = options.pauseCommands || HANDS_FREE_CONFIG.PAUSE_COMMANDS;
        this.resumeCommands = options.resumeCommands || HANDS_FREE_CONFIG.RESUME_COMMANDS;
    }

    /**
     * Detect if transcript contains a pause command
     * @param {string} transcript - The speech transcript to check
     * @returns {boolean} True if pause command detected
     */
    detectPause(transcript) {
        if (!transcript || typeof transcript !== 'string') {
            return false;
        }

        const normalized = transcript.toLowerCase().trim();
        return this.pauseCommands.includes(normalized);
    }

    /**
     * Detect if transcript contains a resume command
     * @param {string} transcript - The speech transcript to check
     * @returns {boolean} True if resume command detected
     */
    detectResume(transcript) {
        if (!transcript || typeof transcript !== 'string') {
            return false;
        }

        const normalized = transcript.toLowerCase().trim();
        return this.resumeCommands.includes(normalized);
    }

    /**
     * Detect any voice command in transcript
     * @param {string} transcript - The speech transcript to check
     * @returns {Object} Detection result with { matched: boolean, command: string|null }
     */
    detect(transcript) {
        if (this.detectPause(transcript)) {
            return { matched: true, command: 'pause' };
        }

        if (this.detectResume(transcript)) {
            return { matched: true, command: 'resume' };
        }

        return { matched: false, command: null };
    }
}
