/**
 * Incremental Speech Module
 *
 * Enables speaking text as it streams in, rather than waiting for the complete response.
 * Buffers incoming text and speaks complete sentences as they're detected.
 *
 * Dependencies:
 * - VoiceSettings module for TTS configuration
 * - Browser speechSynthesis API
 */

import * as VoiceSettings from './voice_settings.js';

// ============================================================
// STATE
// ============================================================

let speechQueue = [];
let isSpeaking = false;
let textBuffer = '';
let isEnabled = true;
let onSpeechComplete = null;

// Voice cache - voices load asynchronously in browsers
let cachedVoices = [];
let voicesLoaded = false;

// Sentence detection pattern: ends with . ! ? followed by space or end of string
const SENTENCE_END_PATTERN = /[.!?](?:\s|$)/;

// Minimum chunk size to speak even without sentence boundary (for very long sentences)
const MIN_CHUNK_SIZE = 150;

// ============================================================
// VOICE LOADING
// ============================================================

/**
 * Ensure voices are loaded before speaking.
 * Browsers load voices asynchronously, so we need to wait.
 */
function ensureVoicesLoaded() {
    return new Promise((resolve) => {
        if (voicesLoaded && cachedVoices.length > 0) {
            resolve(cachedVoices);
            return;
        }

        cachedVoices = window.speechSynthesis.getVoices();
        if (cachedVoices.length > 0) {
            voicesLoaded = true;
            resolve(cachedVoices);
            return;
        }

        // Wait for voiceschanged event
        const handleVoicesChanged = () => {
            cachedVoices = window.speechSynthesis.getVoices();
            if (cachedVoices.length > 0) {
                voicesLoaded = true;
                window.speechSynthesis.removeEventListener('voiceschanged', handleVoicesChanged);
                resolve(cachedVoices);
            }
        };
        window.speechSynthesis.addEventListener('voiceschanged', handleVoicesChanged);

        // Fallback timeout after 2 seconds
        setTimeout(() => {
            if (!voicesLoaded) {
                cachedVoices = window.speechSynthesis.getVoices();
                voicesLoaded = true;
                resolve(cachedVoices);
            }
        }, 2000);
    });
}

// Start loading voices immediately on module load
ensureVoicesLoaded();

// ============================================================
// PUBLIC API
// ============================================================

/**
 * Initialize the incremental speech module.
 * Call this before starting to receive streaming chunks.
 */
export async function initialize() {
    speechQueue = [];
    isSpeaking = false;
    textBuffer = '';
    await ensureVoicesLoaded();
}

/**
 * Enable or disable incremental speech.
 */
export function setEnabled(enabled) {
    isEnabled = enabled;
}

/**
 * Check if incremental speech is enabled.
 */
export function getEnabled() {
    return isEnabled;
}

/**
 * Set callback for when all speech completes.
 */
export function setOnComplete(callback) {
    onSpeechComplete = callback;
}

/**
 * Add a text chunk to the buffer.
 * Will automatically speak complete sentences as they're detected.
 */
export function addChunk(chunk) {
    if (!chunk) return;
    textBuffer += chunk;
    processBuffer();
}

/**
 * Finalize the stream and speak any remaining buffered text.
 */
export function finalize() {
    if (textBuffer.trim()) {
        queueSentence(textBuffer.trim());
        textBuffer = '';
    }
}

/**
 * Stop all speech and clear the queue.
 */
export function stop() {
    window.speechSynthesis.cancel();
    speechQueue = [];
    isSpeaking = false;
    textBuffer = '';
}

/**
 * Check if currently speaking or has queued speech.
 */
export function getIsSpeaking() {
    return isSpeaking || speechQueue.length > 0;
}

/**
 * Reset the module state completely.
 */
export function reset() {
    stop();
    onSpeechComplete = null;
}

// ============================================================
// INTERNAL - BUFFER PROCESSING
// ============================================================

/**
 * Process the text buffer, extracting and queuing complete sentences.
 */
function processBuffer() {
    if (!textBuffer) return;

    let lastIndex = 0;
    const regex = new RegExp(SENTENCE_END_PATTERN, 'g');
    let match;

    while ((match = regex.exec(textBuffer)) !== null) {
        const sentenceEnd = match.index + 1;
        const sentence = textBuffer.slice(lastIndex, sentenceEnd).trim();
        if (sentence) {
            queueSentence(sentence);
        }
        lastIndex = sentenceEnd;
    }

    if (lastIndex > 0) {
        textBuffer = textBuffer.slice(lastIndex).trim();
    }

    // Handle long text without sentence boundaries
    if (textBuffer.length >= MIN_CHUNK_SIZE) {
        const breakMatch = textBuffer.match(/[,;]\s|(?<=\s)\S+$/);
        if (breakMatch) {
            const breakPoint = breakMatch.index + (breakMatch[0].includes(',') || breakMatch[0].includes(';') ? 1 : 0);
            const chunk = textBuffer.slice(0, breakPoint).trim();
            if (chunk) {
                queueSentence(chunk);
            }
            textBuffer = textBuffer.slice(breakPoint).trim();
        }
    }
}

/**
 * Queue a sentence for speaking.
 */
function queueSentence(sentence) {
    speechQueue.push(sentence);
    if (!isSpeaking && isEnabled) {
        speakNext();
    }
}

// ============================================================
// INTERNAL - SPEECH SYNTHESIS
// ============================================================

/**
 * Speak the next sentence in the queue.
 */
function speakNext() {
    if (speechQueue.length === 0) {
        isSpeaking = false;
        if (onSpeechComplete) {
            onSpeechComplete();
        }
        return;
    }

    isSpeaking = true;
    const text = speechQueue.shift();
    const utterance = new SpeechSynthesisUtterance(text);

    // Apply voice settings
    applyVoiceSettings(utterance);

    utterance.onend = () => speakNext();
    utterance.onerror = (event) => {
        console.error('[IncrementalSpeech] Error:', event.error);
        speakNext();
    };

    window.speechSynthesis.speak(utterance);
}

/**
 * Apply user's voice settings to an utterance.
 */
function applyVoiceSettings(utterance) {
    const settings = VoiceSettings.getTTSSettings();

    utterance.rate = settings.rate;
    utterance.pitch = settings.pitch;
    utterance.volume = settings.volume;
    utterance.lang = settings.lang;

    // Apply selected voice
    if (settings.voice) {
        // Refresh cache if needed
        if (cachedVoices.length === 0) {
            cachedVoices = window.speechSynthesis.getVoices();
        }

        const voice = cachedVoices.find(v => v.name === settings.voice);
        if (voice) {
            utterance.voice = voice;
        }
    }
}
