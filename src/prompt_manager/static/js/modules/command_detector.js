/**
 * Command Detector - Detects command word (Ember) followed by specific commands
 *
 * Enables voice command pattern: "Ember, [command]"
 * Examples:
 * - "Ember, repeat that" -> repeat last response
 * - "Ember, transcribe this" -> start transcription
 *
 * This is a pure domain model with no browser API dependencies.
 */

import { HANDS_FREE_CONFIG } from './config.js';

export class CommandDetector {
    /**
     * Create a CommandDetector instance
     * @param {Object} options - Configuration options
     * @param {string} options.commandWord - Command prefix word (default: 'ember')
     * @param {Object} options.commands - Command definitions { commandName: [variations] }
     */
    constructor(options = {}) {
        // Normalize command word to lowercase
        this.commandWord = (options.commandWord || HANDS_FREE_CONFIG.COMMAND_WORD || 'ember').toLowerCase();

        // Default command definitions
        this.commands = options.commands || HANDS_FREE_CONFIG.COMMANDS || {
            'repeat': ['repeat'],
            'transcribe': ['transcribe']
        };
    }

    /**
     * Normalize text for comparison (lowercase, trim, remove punctuation)
     * @param {*} text - Text to normalize
     * @returns {string} Normalized text, or empty string if invalid
     * @private
     */
    _normalize(text) {
        if (typeof text !== 'string') {
            return '';
        }
        // Remove punctuation, lowercase, trim, collapse multiple spaces
        return text
            .toLowerCase()
            .replace(/[^\w\s]/g, ' ')  // Replace punctuation with space
            .trim()
            .replace(/\s+/g, ' ');      // Collapse multiple spaces
    }

    /**
     * Detect command word followed by a command
     * @param {string} transcript - Speech transcript to analyze
     * @returns {Object} Detection result: { matched: boolean, command: string|null }
     */
    detect(transcript) {
        const normalized = this._normalize(transcript);

        if (!normalized) {
            return { matched: false, command: null };
        }

        // Check if starts with command word
        if (!normalized.startsWith(this.commandWord + ' ')) {
            return { matched: false, command: null };
        }

        // Extract the part after command word
        const afterCommandWord = normalized.substring(this.commandWord.length).trim();

        if (!afterCommandWord) {
            return { matched: false, command: null };
        }

        // Check each command definition
        for (const [commandName, variations] of Object.entries(this.commands)) {
            for (const variation of variations) {
                // Check if the text after command word starts with this variation
                if (afterCommandWord === variation || afterCommandWord.startsWith(variation + ' ')) {
                    return { matched: true, command: commandName };
                }
            }
        }

        return { matched: false, command: null };
    }

    /**
     * Get list of supported command names
     * @returns {string[]} Array of command names
     */
    getSupportedCommands() {
        return Object.keys(this.commands);
    }

    /**
     * Check if a command is supported
     * @param {string} commandName - Command name to check
     * @returns {boolean} True if command is supported
     */
    isCommandSupported(commandName) {
        return this.commands.hasOwnProperty(commandName);
    }
}
