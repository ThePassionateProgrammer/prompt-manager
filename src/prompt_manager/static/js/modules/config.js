/**
 * Configuration module for hands-free conversation mode
 * Provides global constants for wake words, silence detection, and other settings
 *
 * Settings are loaded from user_settings.json via /api/settings/hands-free
 */

export const HANDS_FREE_CONFIG = Object.freeze({
    // Default wake/sleep words (overridden by user settings)
    // Include "ember" variations since Chrome often transcribes "Amber" as "Ember"
    DEFAULT_WAKE_WORDS: ['hey amber', 'hi amber', 'amber', 'hey ember', 'hi ember', 'ember'],
    DEFAULT_SLEEP_WORDS: ['sleep amber', 'goodbye amber', 'stop amber', 'sleep ember', 'goodbye ember', 'stop ember'],

    // Voice commands
    PAUSE_COMMANDS: ['amber pause', 'amber, pause', 'pause amber'],
    RESUME_COMMANDS: ['amber resume', 'amber, resume', 'resume amber'],

    // Command word configuration (e.g., "Ember, repeat that")
    COMMAND_WORD: 'ember',
    COMMANDS: {
        'repeat': ['repeat', 'repeat that'],
        'transcribe': ['transcribe', 'transcribe this']
    },

    // Silence detection configuration (in milliseconds)
    DEFAULT_SILENCE_THRESHOLD_MS: 5000,    // 5 seconds - triggers auto-send in hands-free mode
    SILENCE_CHECK_INTERVAL_MS: 100,        // How often to check for silence

    // Matching configuration
    FUZZY_MATCH_ENABLED: false,  // Exact match for V1
    CASE_SENSITIVE: false,

    // Visual feedback
    SHOW_WAKE_LISTENING_STATE: true,
});

// Runtime settings (loaded from user settings)
let runtimeSilenceThreshold = HANDS_FREE_CONFIG.DEFAULT_SILENCE_THRESHOLD_MS;
let runtimeWakeWords = [...HANDS_FREE_CONFIG.DEFAULT_WAKE_WORDS];
let runtimeSleepWords = [...HANDS_FREE_CONFIG.DEFAULT_SLEEP_WORDS];

/**
 * Load hands-free settings from the server
 * @returns {Promise<void>}
 */
export async function loadHandsFreeSettings() {
    try {
        const response = await fetch('/api/settings/hands-free');
        if (response.ok) {
            const data = await response.json();
            // Convert seconds to milliseconds
            runtimeSilenceThreshold = data.auto_send_timeout * 1000;
            // Load wake/sleep words
            if (data.wake_words && data.wake_words.length > 0) {
                runtimeWakeWords = data.wake_words;
            }
            if (data.sleep_words && data.sleep_words.length > 0) {
                runtimeSleepWords = data.sleep_words;
            }
            console.log('[Config] Loaded hands-free settings:', {
                timeout: data.auto_send_timeout + 's',
                wakeWords: runtimeWakeWords,
                sleepWords: runtimeSleepWords
            });
        }
    } catch (error) {
        console.error('[Config] Error loading hands-free settings:', error);
        // Fall back to defaults
        runtimeSilenceThreshold = HANDS_FREE_CONFIG.DEFAULT_SILENCE_THRESHOLD_MS;
        runtimeWakeWords = [...HANDS_FREE_CONFIG.DEFAULT_WAKE_WORDS];
        runtimeSleepWords = [...HANDS_FREE_CONFIG.DEFAULT_SLEEP_WORDS];
    }
}

/**
 * Get the current silence threshold in milliseconds
 * @returns {number} Silence threshold in milliseconds
 */
export function getSilenceThreshold() {
    return runtimeSilenceThreshold;
}

/**
 * Get the wake word (backward compatible - returns first word)
 * @returns {string} Wake word phrase
 */
export function getWakeWord() {
    return runtimeWakeWords[0];
}

/**
 * Get all wake words
 * @returns {string[]} Array of wake word phrases
 */
export function getWakeWords() {
    return runtimeWakeWords;
}

/**
 * Get the sleep word (backward compatible - returns first word)
 * @returns {string} Sleep word phrase
 */
export function getSleepWord() {
    return runtimeSleepWords[0];
}

/**
 * Get all sleep words
 * @returns {string[]} Array of sleep word phrases
 */
export function getSleepWords() {
    return runtimeSleepWords;
}
