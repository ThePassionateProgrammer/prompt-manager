/**
 * Voice Settings Module
 *
 * Manages user preferences for text-to-speech and speech recognition.
 * Allows customization of voice, rate, pitch, and recognition language.
 *
 * Settings are persisted to localStorage and applied to voice interactions.
 */

const STORAGE_KEY = 'voiceSettings';

// Default settings
const defaultSettings = {
    tts: {
        rate: 1.0,          // Speech rate: 0.1 to 10
        pitch: 1.0,         // Voice pitch: 0 to 2
        volume: 1.0,        // Volume: 0 to 1
        voice: null,        // Voice name (null = system default)
        lang: 'en-US'       // Language code
    },
    stt: {
        lang: 'en-US',      // Recognition language
        continuous: true,   // Continuous recognition in conversation mode
        interimResults: false  // Show interim results
    }
};

// Current settings (loaded from storage or defaults)
let settings = { ...defaultSettings };

/**
 * Initialize voice settings module.
 * Loads settings from localStorage.
 */
export function initializeVoiceSettings() {
    loadSettings();
}

/**
 * Load settings from localStorage.
 */
function loadSettings() {
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
            const parsed = JSON.parse(stored);
            settings = {
                tts: { ...defaultSettings.tts, ...parsed.tts },
                stt: { ...defaultSettings.stt, ...parsed.stt }
            };
        }
    } catch (error) {
        console.error('Error loading voice settings:', error);
        settings = { ...defaultSettings };
    }
}

/**
 * Save settings to localStorage.
 */
function saveSettings() {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
    } catch (error) {
        console.error('Error saving voice settings:', error);
    }
}

/**
 * Get current TTS settings.
 *
 * @returns {Object} TTS settings
 */
export function getTTSSettings() {
    return { ...settings.tts };
}

/**
 * Get current STT (speech recognition) settings.
 *
 * @returns {Object} STT settings
 */
export function getSTTSettings() {
    return { ...settings.stt };
}

/**
 * Update TTS settings.
 *
 * @param {Object} newSettings - New TTS settings (partial)
 */
export function updateTTSSettings(newSettings) {
    settings.tts = { ...settings.tts, ...newSettings };
    saveSettings();
}

/**
 * Update STT settings.
 *
 * @param {Object} newSettings - New STT settings (partial)
 */
export function updateSTTSettings(newSettings) {
    settings.stt = { ...settings.stt, ...newSettings };
    saveSettings();
}

/**
 * Reset all settings to defaults.
 */
export function resetToDefaults() {
    settings = JSON.parse(JSON.stringify(defaultSettings));
    saveSettings();
}

/**
 * Get available voices from the browser.
 *
 * @returns {Promise<Array>} Array of available voices
 */
export function getAvailableVoices() {
    return new Promise((resolve) => {
        let voices = speechSynthesis.getVoices();

        if (voices.length > 0) {
            resolve(voices);
        } else {
            // Voices may load asynchronously
            speechSynthesis.onvoiceschanged = () => {
                voices = speechSynthesis.getVoices();
                resolve(voices);
            };
        }
    });
}

/**
 * Get voices filtered by language.
 *
 * @param {string} lang - Language code (e.g., 'en-US')
 * @returns {Promise<Array>} Filtered voices
 */
export async function getVoicesForLanguage(lang) {
    const voices = await getAvailableVoices();
    return voices.filter(voice => voice.lang === lang);
}

/**
 * Apply TTS settings to a SpeechSynthesisUtterance.
 *
 * @param {SpeechSynthesisUtterance} utterance - Utterance to configure
 */
export async function applyTTSSettings(utterance) {
    const ttsSettings = getTTSSettings();

    utterance.rate = ttsSettings.rate;
    utterance.pitch = ttsSettings.pitch;
    utterance.volume = ttsSettings.volume;
    utterance.lang = ttsSettings.lang;

    // Apply selected voice if specified
    if (ttsSettings.voice) {
        const voices = await getAvailableVoices();
        const selectedVoice = voices.find(v => v.name === ttsSettings.voice);
        if (selectedVoice) {
            utterance.voice = selectedVoice;
        }
    }
}

/**
 * Apply STT settings to a SpeechRecognition instance.
 *
 * @param {SpeechRecognition} recognition - Recognition instance to configure
 */
export function applySTTSettings(recognition) {
    const sttSettings = getSTTSettings();

    recognition.lang = sttSettings.lang;
    recognition.interimResults = sttSettings.interimResults;
    // Note: continuous mode is managed by conversation mode state
}

/**
 * Create a settings UI panel (returns HTML element).
 *
 * @returns {HTMLElement} Settings panel element
 */
export function createSettingsPanel() {
    const panel = document.createElement('div');
    panel.className = 'voice-settings-panel';
    panel.innerHTML = `
        <h3>Voice Settings</h3>

        <div class="settings-section">
            <h4>Text-to-Speech</h4>

            <div class="setting-item">
                <label for="tts-rate">Speech Rate: <span id="tts-rate-value">${settings.tts.rate}</span></label>
                <input type="range" id="tts-rate" min="0.5" max="2" step="0.1" value="${settings.tts.rate}">
            </div>

            <div class="setting-item">
                <label for="tts-pitch">Pitch: <span id="tts-pitch-value">${settings.tts.pitch}</span></label>
                <input type="range" id="tts-pitch" min="0.5" max="2" step="0.1" value="${settings.tts.pitch}">
            </div>

            <div class="setting-item">
                <label for="tts-volume">Volume: <span id="tts-volume-value">${settings.tts.volume}</span></label>
                <input type="range" id="tts-volume" min="0" max="1" step="0.1" value="${settings.tts.volume}">
            </div>

            <div class="setting-item">
                <label for="tts-voice">Voice:</label>
                <select id="tts-voice">
                    <option value="">Default</option>
                </select>
            </div>
        </div>

        <div class="settings-section">
            <h4>Speech Recognition</h4>

            <div class="setting-item">
                <label for="stt-lang">Language:</label>
                <select id="stt-lang">
                    <option value="en-US" ${settings.stt.lang === 'en-US' ? 'selected' : ''}>English (US)</option>
                    <option value="en-GB" ${settings.stt.lang === 'en-GB' ? 'selected' : ''}>English (UK)</option>
                    <option value="es-ES" ${settings.stt.lang === 'es-ES' ? 'selected' : ''}>Spanish</option>
                    <option value="fr-FR" ${settings.stt.lang === 'fr-FR' ? 'selected' : ''}>French</option>
                    <option value="de-DE" ${settings.stt.lang === 'de-DE' ? 'selected' : ''}>German</option>
                    <option value="it-IT" ${settings.stt.lang === 'it-IT' ? 'selected' : ''}>Italian</option>
                    <option value="pt-BR" ${settings.stt.lang === 'pt-BR' ? 'selected' : ''}>Portuguese (BR)</option>
                    <option value="ja-JP" ${settings.stt.lang === 'ja-JP' ? 'selected' : ''}>Japanese</option>
                    <option value="zh-CN" ${settings.stt.lang === 'zh-CN' ? 'selected' : ''}>Chinese (Simplified)</option>
                </select>
            </div>
        </div>

        <div class="settings-actions">
            <button id="reset-voice-settings" class="btn-secondary">Reset to Defaults</button>
            <button id="test-voice-settings" class="btn-primary">Test Voice</button>
        </div>
    `;

    // Set up event listeners
    setupSettingsListeners(panel);

    // Load available voices
    loadVoicesIntoSelect(panel);

    return panel;
}

/**
 * Set up event listeners for settings panel.
 *
 * @param {HTMLElement} panel - Settings panel element
 */
function setupSettingsListeners(panel) {
    // TTS Rate
    const rateSlider = panel.querySelector('#tts-rate');
    const rateValue = panel.querySelector('#tts-rate-value');
    rateSlider.addEventListener('input', (e) => {
        const value = parseFloat(e.target.value);
        rateValue.textContent = value.toFixed(1);
        updateTTSSettings({ rate: value });
    });

    // TTS Pitch
    const pitchSlider = panel.querySelector('#tts-pitch');
    const pitchValue = panel.querySelector('#tts-pitch-value');
    pitchSlider.addEventListener('input', (e) => {
        const value = parseFloat(e.target.value);
        pitchValue.textContent = value.toFixed(1);
        updateTTSSettings({ pitch: value });
    });

    // TTS Volume
    const volumeSlider = panel.querySelector('#tts-volume');
    const volumeValue = panel.querySelector('#tts-volume-value');
    volumeSlider.addEventListener('input', (e) => {
        const value = parseFloat(e.target.value);
        volumeValue.textContent = value.toFixed(1);
        updateTTSSettings({ volume: value });
    });

    // TTS Voice
    const voiceSelect = panel.querySelector('#tts-voice');
    voiceSelect.addEventListener('change', (e) => {
        updateTTSSettings({ voice: e.target.value || null });
    });

    // STT Language
    const langSelect = panel.querySelector('#stt-lang');
    langSelect.addEventListener('change', (e) => {
        updateSTTSettings({ lang: e.target.value });
    });

    // Reset button
    const resetBtn = panel.querySelector('#reset-voice-settings');
    resetBtn.addEventListener('click', () => {
        resetToDefaults();
        // Recreate panel to reflect defaults
        const newPanel = createSettingsPanel();
        panel.replaceWith(newPanel);
    });

    // Test button
    const testBtn = panel.querySelector('#test-voice-settings');
    testBtn.addEventListener('click', async () => {
        const utterance = new SpeechSynthesisUtterance('This is a test of the current voice settings.');
        await applyTTSSettings(utterance);
        speechSynthesis.speak(utterance);
    });
}

/**
 * Load available voices into the voice select dropdown.
 *
 * @param {HTMLElement} panel - Settings panel element
 */
async function loadVoicesIntoSelect(panel) {
    const voiceSelect = panel.querySelector('#tts-voice');
    const voices = await getAvailableVoices();

    // Clear existing options except default
    voiceSelect.innerHTML = '<option value="">Default</option>';

    // Add voices
    voices.forEach(voice => {
        const option = document.createElement('option');
        option.value = voice.name;
        option.textContent = `${voice.name} (${voice.lang})`;
        if (voice.name === settings.tts.voice) {
            option.selected = true;
        }
        voiceSelect.appendChild(option);
    });
}
