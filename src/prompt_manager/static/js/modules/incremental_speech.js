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

// Speech state
let speechQueue = [];
let isSpeaking = false;
let textBuffer = '';
let isEnabled = true;
let onSpeechComplete = null;

// Cached voices (loaded asynchronously by browser)
let cachedVoices = [];
let voicesLoaded = false;

/**
 * Ensure voices are loaded before speaking.
 * Returns a promise that resolves when voices are available.
 */
function ensureVoicesLoaded() {
    return new Promise((resolve) => {
        // If already loaded, return immediately
        if (voicesLoaded && cachedVoices.length > 0) {
            resolve(cachedVoices);
            return;
        }

        // Try to get voices
        cachedVoices = window.speechSynthesis.getVoices();
        if (cachedVoices.length > 0) {
            voicesLoaded = true;
            console.log('[IncrementalSpeech] Voices loaded:', cachedVoices.length);
            resolve(cachedVoices);
            return;
        }

        // Voices not ready yet - wait for voiceschanged event
        console.log('[IncrementalSpeech] Waiting for voices to load...');
        const handleVoicesChanged = () => {
            cachedVoices = window.speechSynthesis.getVoices();
            if (cachedVoices.length > 0) {
                voicesLoaded = true;
                console.log('[IncrementalSpeech] Voices loaded after wait:', cachedVoices.length);
                window.speechSynthesis.removeEventListener('voiceschanged', handleVoicesChanged);
                resolve(cachedVoices);
            }
        };
        window.speechSynthesis.addEventListener('voiceschanged', handleVoicesChanged);

        // Fallback timeout - resolve anyway after 2 seconds
        setTimeout(() => {
            if (!voicesLoaded) {
                cachedVoices = window.speechSynthesis.getVoices();
                voicesLoaded = true;
                console.log('[IncrementalSpeech] Voices timeout, have:', cachedVoices.length);
                resolve(cachedVoices);
            }
        }, 2000);
    });
}

// Start loading voices immediately
ensureVoicesLoaded();

// Sentence detection pattern: ends with . ! ? followed by space or end of string
const SENTENCE_END_PATTERN = /[.!?](?:\s|$)/;

// Minimum chunk size to speak even without sentence boundary (for very long sentences)
const MIN_CHUNK_SIZE = 150;

/**
 * Initialize the incremental speech module.
 * Call this before starting to receive streaming chunks.
 */
export async function initialize() {
    speechQueue = [];
    isSpeaking = false;
    textBuffer = '';

    // Ensure voices are loaded before speaking
    await ensureVoicesLoaded();
}

/**
 * Enable or disable incremental speech.
 * When disabled, text is buffered but not spoken.
 *
 * @param {boolean} enabled - Whether to enable incremental speech
 */
export function setEnabled(enabled) {
    isEnabled = enabled;
}

/**
 * Check if incremental speech is enabled.
 *
 * @returns {boolean} True if enabled
 */
export function getEnabled() {
    return isEnabled;
}

/**
 * Set callback for when all speech completes.
 *
 * @param {Function} callback - Function to call when speech queue empties
 */
export function setOnComplete(callback) {
    onSpeechComplete = callback;
}

/**
 * Add a text chunk to the buffer.
 * Will automatically speak complete sentences as they're detected.
 *
 * @param {string} chunk - Text chunk to add
 */
export function addChunk(chunk) {
    if (!chunk) return;

    textBuffer += chunk;

    // Check for sentence boundaries and queue complete sentences
    processBuffer();
}

/**
 * Process the text buffer, extracting and queuing complete sentences.
 */
function processBuffer() {
    if (!textBuffer) return;

    // Find sentence boundaries
    let match;
    let lastIndex = 0;

    // Use regex to find all sentence endings
    const regex = new RegExp(SENTENCE_END_PATTERN, 'g');

    while ((match = regex.exec(textBuffer)) !== null) {
        // Extract the sentence (including punctuation)
        const sentenceEnd = match.index + 1; // Include the punctuation
        const sentence = textBuffer.slice(lastIndex, sentenceEnd).trim();

        if (sentence) {
            queueSentence(sentence);
        }

        lastIndex = sentenceEnd;
    }

    // Keep any remaining text in buffer
    if (lastIndex > 0) {
        textBuffer = textBuffer.slice(lastIndex).trim();
    }

    // If buffer is getting long without sentence boundaries, speak it anyway
    if (textBuffer.length >= MIN_CHUNK_SIZE) {
        // Find a natural break point (comma, semicolon, or word boundary)
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
 *
 * @param {string} sentence - Sentence to speak
 */
function queueSentence(sentence) {
    speechQueue.push(sentence);

    // Start speaking if not already speaking and enabled
    if (!isSpeaking && isEnabled) {
        speakNext();
    }
}

/**
 * Speak the next sentence in the queue.
 * Applies voice settings synchronously to avoid async timing issues.
 */
function speakNext() {
    if (speechQueue.length === 0) {
        isSpeaking = false;

        // Notify completion if callback set
        if (onSpeechComplete) {
            onSpeechComplete();
        }
        return;
    }

    isSpeaking = true;
    const text = speechQueue.shift();

    const utterance = new SpeechSynthesisUtterance(text);

    // Apply user's voice settings synchronously (get fresh settings each time)
    const ttsSettings = VoiceSettings.getTTSSettings();
    console.log('[IncrementalSpeech] Applying TTS - rate:', ttsSettings.rate, 'pitch:', ttsSettings.pitch, 'volume:', ttsSettings.volume, 'voice:', ttsSettings.voice);
    utterance.rate = ttsSettings.rate;
    utterance.pitch = ttsSettings.pitch;
    utterance.volume = ttsSettings.volume;
    utterance.lang = ttsSettings.lang;
    console.log('[IncrementalSpeech] Utterance after settings - rate:', utterance.rate, 'pitch:', utterance.pitch);

    // Apply selected voice if specified
    if (ttsSettings.voice) {
        // Refresh voice cache if empty (fallback)
        if (cachedVoices.length === 0) {
            cachedVoices = window.speechSynthesis.getVoices();
            console.log('[IncrementalSpeech] Refreshed voices:', cachedVoices.length);
        }

        const selectedVoice = cachedVoices.find(v => v.name === ttsSettings.voice);
        if (selectedVoice) {
            utterance.voice = selectedVoice;
            console.log('[IncrementalSpeech] Using voice:', selectedVoice.name);
        } else {
            console.log('[IncrementalSpeech] Voice not found:', ttsSettings.voice, 'Available:', cachedVoices.length, cachedVoices.map(v => v.name).slice(0, 5));
        }
    }

    utterance.onend = () => {
        // Speak next sentence
        speakNext();
    };

    utterance.onerror = (event) => {
        console.error('Speech synthesis error:', event);
        // Continue with next sentence even on error
        speakNext();
    };

    window.speechSynthesis.speak(utterance);
}

/**
 * Finalize the stream and speak any remaining buffered text.
 * Call this when the streaming response completes.
 */
export function finalize() {
    // Speak any remaining buffered text
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
 * Check if currently speaking.
 *
 * @returns {boolean} True if speaking
 */
export function getIsSpeaking() {
    return isSpeaking || speechQueue.length > 0;
}

/**
 * Reset the module state.
 * Stops any speech and clears all buffers.
 */
export function reset() {
    stop();
    onSpeechComplete = null;
}
