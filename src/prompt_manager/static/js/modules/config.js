/**
 * Configuration module for hands-free conversation mode
 * Provides global constants for wake words, silence detection, and other settings
 */

export const HANDS_FREE_CONFIG = Object.freeze({
    // Wake word configuration
    WAKE_WORD: 'hey amber',
    SLEEP_WORD: 'sleep amber',

    // Voice commands
    PAUSE_COMMANDS: ['amber pause', 'amber, pause', 'pause amber'],
    RESUME_COMMANDS: ['amber resume', 'amber, resume', 'resume amber'],

    // Silence detection configuration (in milliseconds)
    DEFAULT_SILENCE_THRESHOLD_MS: 3000,
    EXTENDED_SILENCE_THRESHOLD_MS: 10000,  // Auto-pause after this duration
    SILENCE_CHECK_INTERVAL_MS: 100,        // How often to check for silence

    // Matching configuration
    FUZZY_MATCH_ENABLED: false,  // Exact match for V1
    CASE_SENSITIVE: false,

    // Visual feedback
    SHOW_WAKE_LISTENING_STATE: true,
});

// Runtime silence threshold (loaded from user settings)
let runtimeSilenceThreshold = HANDS_FREE_CONFIG.DEFAULT_SILENCE_THRESHOLD_MS;

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
            console.log('[Config] Loaded hands-free timeout:', data.auto_send_timeout, 'seconds');
        }
    } catch (error) {
        console.error('[Config] Error loading hands-free settings:', error);
        // Fall back to default
        runtimeSilenceThreshold = HANDS_FREE_CONFIG.DEFAULT_SILENCE_THRESHOLD_MS;
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
 * Get the wake word
 * @returns {string} Wake word phrase
 */
export function getWakeWord() {
    return HANDS_FREE_CONFIG.WAKE_WORD;
}

/**
 * Get the sleep word
 * @returns {string} Sleep word phrase
 */
export function getSleepWord() {
    return HANDS_FREE_CONFIG.SLEEP_WORD;
}
