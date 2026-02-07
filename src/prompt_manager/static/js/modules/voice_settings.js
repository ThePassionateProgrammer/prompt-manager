/**
 * Voice Settings Module
 *
 * Manages user preferences for text-to-speech and speech recognition.
 * Settings are persisted to localStorage and applied to voice interactions.
 */

const STORAGE_KEY = 'voiceSettings';

// ============================================================
// DEFAULT SETTINGS
// ============================================================

const defaultSettings = {
    tts: {
        rate: 1.0,          // Speech rate: 0.5 to 2
        pitch: 1.0,         // Voice pitch: 0.5 to 2
        volume: 1.0,        // Volume: 0 to 1
        voice: null,        // Voice name (null = system default)
        lang: 'en-US'       // Language code
    },
    stt: {
        lang: 'en-US',      // Recognition language
        continuous: true,   // Continuous recognition in conversation mode
        interimResults: false
    }
};

// Current settings (deep copy to avoid mutation)
let settings = {
    tts: { ...defaultSettings.tts },
    stt: { ...defaultSettings.stt }
};

// ============================================================
// INITIALIZATION & PERSISTENCE
// ============================================================

/**
 * Initialize voice settings module. Loads settings from localStorage.
 */
export function initializeVoiceSettings() {
    loadSettings();
}

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
        console.error('[VoiceSettings] Error loading:', error);
        settings = {
            tts: { ...defaultSettings.tts },
            stt: { ...defaultSettings.stt }
        };
    }
}

function saveSettings() {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
    } catch (error) {
        console.error('[VoiceSettings] Error saving:', error);
    }
}

// ============================================================
// GETTERS & SETTERS
// ============================================================

export function getTTSSettings() {
    return { ...settings.tts };
}

export function getSTTSettings() {
    return { ...settings.stt };
}

export function updateTTSSettings(newSettings) {
    settings.tts = { ...settings.tts, ...newSettings };
    saveSettings();
}

export function updateSTTSettings(newSettings) {
    settings.stt = { ...settings.stt, ...newSettings };
    saveSettings();
}

export function resetToDefaults() {
    settings = JSON.parse(JSON.stringify(defaultSettings));
    saveSettings();
}

// ============================================================
// VOICE UTILITIES
// ============================================================

/**
 * Get available voices from the browser (async - voices load lazily).
 */
export function getAvailableVoices() {
    return new Promise((resolve) => {
        let voices = speechSynthesis.getVoices();
        if (voices.length > 0) {
            resolve(voices);
        } else {
            speechSynthesis.onvoiceschanged = () => {
                resolve(speechSynthesis.getVoices());
            };
        }
    });
}

/**
 * Apply TTS settings to a SpeechSynthesisUtterance.
 */
export async function applyTTSSettings(utterance) {
    const tts = getTTSSettings();

    utterance.rate = tts.rate;
    utterance.pitch = tts.pitch;
    utterance.volume = tts.volume;
    utterance.lang = tts.lang;

    if (tts.voice) {
        const voices = await getAvailableVoices();
        const voice = voices.find(v => v.name === tts.voice);
        if (voice) {
            utterance.voice = voice;
        }
    }
}

/**
 * Apply STT settings to a SpeechRecognition instance.
 */
export function applySTTSettings(recognition) {
    const stt = getSTTSettings();
    recognition.lang = stt.lang;
    recognition.interimResults = stt.interimResults;
}

// ============================================================
// SETTINGS UI
// ============================================================

/**
 * Create a settings UI panel.
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
                    <option value="">System Default</option>
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
                </select>
            </div>
        </div>

        <div class="settings-actions">
            <button id="reset-voice-settings" class="btn-secondary">Reset to Defaults</button>
            <button id="test-voice-settings" class="btn-primary">Test Voice</button>
        </div>
    `;

    setupSettingsListeners(panel);
    loadVoicesIntoSelect(panel);

    return panel;
}

function setupSettingsListeners(panel) {
    // Rate slider
    const rateSlider = panel.querySelector('#tts-rate');
    const rateValue = panel.querySelector('#tts-rate-value');
    rateSlider.addEventListener('input', (e) => {
        const value = parseFloat(e.target.value);
        rateValue.textContent = value.toFixed(1);
        updateTTSSettings({ rate: value });
    });

    // Pitch slider
    const pitchSlider = panel.querySelector('#tts-pitch');
    const pitchValue = panel.querySelector('#tts-pitch-value');
    pitchSlider.addEventListener('input', (e) => {
        const value = parseFloat(e.target.value);
        pitchValue.textContent = value.toFixed(1);
        updateTTSSettings({ pitch: value });
    });

    // Volume slider
    const volumeSlider = panel.querySelector('#tts-volume');
    const volumeValue = panel.querySelector('#tts-volume-value');
    volumeSlider.addEventListener('input', (e) => {
        const value = parseFloat(e.target.value);
        volumeValue.textContent = value.toFixed(1);
        updateTTSSettings({ volume: value });
    });

    // Voice select
    panel.querySelector('#tts-voice').addEventListener('change', (e) => {
        updateTTSSettings({ voice: e.target.value || null });
    });

    // Language select
    panel.querySelector('#stt-lang').addEventListener('change', (e) => {
        updateSTTSettings({ lang: e.target.value });
        // Reload voices for new language
        loadVoicesIntoSelect(panel);
    });

    // Reset button
    panel.querySelector('#reset-voice-settings').addEventListener('click', () => {
        resetToDefaults();
        const newPanel = createSettingsPanel();
        panel.replaceWith(newPanel);
    });

    // Test button
    panel.querySelector('#test-voice-settings').addEventListener('click', async () => {
        const utterance = new SpeechSynthesisUtterance('This is a test of the current voice settings.');
        await applyTTSSettings(utterance);
        speechSynthesis.speak(utterance);
    });
}

// ============================================================
// VOICE LIST HELPERS
// ============================================================

function isHighQualityVoice(voice) {
    const name = voice.name.toLowerCase();
    return ['enhanced', 'premium', 'neural', 'natural', 'wavenet', 'studio'].some(
        indicator => name.includes(indicator)
    );
}

function getVoiceQualityLabel(voice) {
    const name = voice.name.toLowerCase();
    if (name.includes('neural') || name.includes('wavenet')) return '✨';
    if (name.includes('enhanced') || name.includes('premium')) return '⭐';
    if (name.includes('natural')) return '🎯';
    return '';
}

async function loadVoicesIntoSelect(panel) {
    const voiceSelect = panel.querySelector('#tts-voice');
    const voices = await getAvailableVoices();
    const langPrefix = settings.tts.lang.split('-')[0]; // 'en-US' -> 'en'

    // Clear and add default
    voiceSelect.innerHTML = '<option value="">System Default</option>';

    // Filter to current language only
    const matching = voices.filter(v => v.lang.split('-')[0] === langPrefix);

    // Sort: high-quality first, then alphabetically
    const sorted = [...matching].sort((a, b) => {
        const aHQ = isHighQualityVoice(a);
        const bHQ = isHighQualityVoice(b);
        if (aHQ && !bHQ) return -1;
        if (!aHQ && bHQ) return 1;
        return a.name.localeCompare(b.name);
    });

    // Add high-quality voices
    const hqVoices = sorted.filter(isHighQualityVoice);
    if (hqVoices.length > 0) {
        const group = document.createElement('optgroup');
        group.label = '⭐ High Quality';
        hqVoices.forEach(voice => {
            const option = document.createElement('option');
            option.value = voice.name;
            option.textContent = `${voice.name} ${getVoiceQualityLabel(voice)}`;
            option.selected = voice.name === settings.tts.voice;
            group.appendChild(option);
        });
        voiceSelect.appendChild(group);
    }

    // Add standard voices
    const stdVoices = sorted.filter(v => !isHighQualityVoice(v));
    if (stdVoices.length > 0) {
        const group = document.createElement('optgroup');
        group.label = 'Standard';
        stdVoices.forEach(voice => {
            const option = document.createElement('option');
            option.value = voice.name;
            option.textContent = voice.name;
            option.selected = voice.name === settings.tts.voice;
            group.appendChild(option);
        });
        voiceSelect.appendChild(group);
    }
}
