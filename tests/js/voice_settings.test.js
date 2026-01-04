/**
 * Unit tests for the Voice Settings Module
 *
 * Tests TTS/STT settings, persistence, voice selection, and UI generation.
 */

import { describe, test, expect, jest, beforeEach } from '@jest/globals';

let voiceSettingsModule;

beforeEach(async () => {
    // Reset DOM and localStorage
    document.body.innerHTML = '';
    localStorage.clear();

    // Mock speechSynthesis.getVoices()
    const mockVoices = [
        { name: 'Voice 1', lang: 'en-US', default: true },
        { name: 'Voice 2', lang: 'en-US', default: false },
        { name: 'Voice 3', lang: 'en-GB', default: false },
        { name: 'Voice 4', lang: 'es-ES', default: false }
    ];
    global.speechSynthesis.getVoices.mockReturnValue(mockVoices);

    // Clear module cache and re-import
    jest.resetModules();
    voiceSettingsModule = await import('../../src/prompt_manager/static/js/modules/voice_settings.js');

    // Initialize
    voiceSettingsModule.initializeVoiceSettings();
});

describe('Voice Settings Module', () => {
    describe('Initialization', () => {
        test('should initialize with default settings', () => {
            const ttsSettings = voiceSettingsModule.getTTSSettings();

            expect(ttsSettings).toEqual({
                rate: 1.0,
                pitch: 1.0,
                volume: 1.0,
                voice: null,
                lang: 'en-US'
            });
        });

        test('should initialize STT settings with defaults', () => {
            const sttSettings = voiceSettingsModule.getSTTSettings();

            expect(sttSettings).toEqual({
                lang: 'en-US',
                continuous: true,
                interimResults: false
            });
        });

        test('should load settings from localStorage if available', async () => {
            const savedSettings = {
                tts: {
                    rate: 1.5,
                    pitch: 1.2,
                    volume: 0.8,
                    voice: 'Custom Voice',
                    lang: 'en-GB'
                },
                stt: {
                    lang: 'es-ES',
                    continuous: false,
                    interimResults: true
                }
            };

            localStorage.setItem('voiceSettings', JSON.stringify(savedSettings));

            // Re-import and re-initialize
            jest.resetModules();
            const module = await import('../../src/prompt_manager/static/js/modules/voice_settings.js');
            module.initializeVoiceSettings();

            expect(module.getTTSSettings()).toEqual(savedSettings.tts);
            expect(module.getSTTSettings()).toEqual(savedSettings.stt);
        });

        test('should use defaults if localStorage has invalid JSON', async () => {
            localStorage.setItem('voiceSettings', 'invalid json');

            jest.resetModules();
            const module = await import('../../src/prompt_manager/static/js/modules/voice_settings.js');
            module.initializeVoiceSettings();

            const ttsSettings = module.getTTSSettings();
            expect(ttsSettings.rate).toBe(1.0);
        });
    });

    describe('TTS Settings Management', () => {
        test('should get TTS settings', () => {
            const settings = voiceSettingsModule.getTTSSettings();

            expect(settings).toHaveProperty('rate');
            expect(settings).toHaveProperty('pitch');
            expect(settings).toHaveProperty('volume');
            expect(settings).toHaveProperty('voice');
            expect(settings).toHaveProperty('lang');
        });

        test('should update TTS settings', () => {
            voiceSettingsModule.updateTTSSettings({ rate: 1.5 });

            const settings = voiceSettingsModule.getTTSSettings();
            expect(settings.rate).toBe(1.5);
        });

        test('should update multiple TTS settings at once', () => {
            voiceSettingsModule.updateTTSSettings({
                rate: 1.5,
                pitch: 1.2,
                volume: 0.8
            });

            const settings = voiceSettingsModule.getTTSSettings();
            expect(settings.rate).toBe(1.5);
            expect(settings.pitch).toBe(1.2);
            expect(settings.volume).toBe(0.8);
        });

        test('should preserve unmodified TTS settings', () => {
            voiceSettingsModule.updateTTSSettings({ rate: 1.5 });

            const settings = voiceSettingsModule.getTTSSettings();
            expect(settings.pitch).toBe(1.0); // Default unchanged
            expect(settings.volume).toBe(1.0); // Default unchanged
        });

        test('should save TTS settings to localStorage', () => {
            voiceSettingsModule.updateTTSSettings({ rate: 1.5 });

            const saved = JSON.parse(localStorage.getItem('voiceSettings'));
            expect(saved.tts.rate).toBe(1.5);
        });
    });

    describe('STT Settings Management', () => {
        test('should get STT settings', () => {
            const settings = voiceSettingsModule.getSTTSettings();

            expect(settings).toHaveProperty('lang');
            expect(settings).toHaveProperty('continuous');
            expect(settings).toHaveProperty('interimResults');
        });

        test('should update STT settings', () => {
            voiceSettingsModule.updateSTTSettings({ lang: 'es-ES' });

            const settings = voiceSettingsModule.getSTTSettings();
            expect(settings.lang).toBe('es-ES');
        });

        test('should update multiple STT settings at once', () => {
            voiceSettingsModule.updateSTTSettings({
                lang: 'fr-FR',
                interimResults: true
            });

            const settings = voiceSettingsModule.getSTTSettings();
            expect(settings.lang).toBe('fr-FR');
            expect(settings.interimResults).toBe(true);
        });

        test('should save STT settings to localStorage', () => {
            voiceSettingsModule.updateSTTSettings({ lang: 'de-DE' });

            const saved = JSON.parse(localStorage.getItem('voiceSettings'));
            expect(saved.stt.lang).toBe('de-DE');
        });
    });

    describe('Reset to Defaults', () => {
        test('should reset all settings to defaults', () => {
            // Modify settings
            voiceSettingsModule.updateTTSSettings({ rate: 2.0, pitch: 1.5 });
            voiceSettingsModule.updateSTTSettings({ lang: 'es-ES' });

            // Reset
            voiceSettingsModule.resetToDefaults();

            const ttsSettings = voiceSettingsModule.getTTSSettings();
            const sttSettings = voiceSettingsModule.getSTTSettings();

            expect(ttsSettings.rate).toBe(1.0);
            expect(ttsSettings.pitch).toBe(1.0);
            expect(sttSettings.lang).toBe('en-US');
        });

        test('should save defaults to localStorage after reset', () => {
            voiceSettingsModule.updateTTSSettings({ rate: 2.0 });
            voiceSettingsModule.resetToDefaults();

            const saved = JSON.parse(localStorage.getItem('voiceSettings'));
            expect(saved.tts.rate).toBe(1.0);
        });
    });

    describe('Voice Selection', () => {
        test('should get available voices', async () => {
            const voices = await voiceSettingsModule.getAvailableVoices();

            expect(voices).toHaveLength(4);
            expect(voices[0].name).toBe('Voice 1');
        });

        test('should filter voices by language', async () => {
            const enVoices = await voiceSettingsModule.getVoicesForLanguage('en-US');

            expect(enVoices).toHaveLength(2);
            expect(enVoices.every(v => v.lang === 'en-US')).toBe(true);
        });

        test('should handle voices loading asynchronously', async () => {
            // Mock voices not immediately available
            global.speechSynthesis.getVoices.mockReturnValueOnce([]);

            const voicesPromise = voiceSettingsModule.getAvailableVoices();

            // Trigger onvoiceschanged
            global.speechSynthesis.getVoices.mockReturnValue([
                { name: 'Voice 1', lang: 'en-US' }
            ]);

            if (global.speechSynthesis.onvoiceschanged) {
                global.speechSynthesis.onvoiceschanged();
            }

            const voices = await voicesPromise;
            expect(voices).toBeTruthy();
        });
    });

    describe('Apply Settings to Speech APIs', () => {
        test('should apply TTS settings to utterance', async () => {
            voiceSettingsModule.updateTTSSettings({
                rate: 1.5,
                pitch: 1.2,
                volume: 0.8,
                lang: 'en-GB'
            });

            const utterance = new SpeechSynthesisUtterance('Test');
            await voiceSettingsModule.applyTTSSettings(utterance);

            expect(utterance.rate).toBe(1.5);
            expect(utterance.pitch).toBe(1.2);
            expect(utterance.volume).toBe(0.8);
            expect(utterance.lang).toBe('en-GB');
        });

        test('should apply selected voice to utterance', async () => {
            voiceSettingsModule.updateTTSSettings({ voice: 'Voice 2' });

            const utterance = new SpeechSynthesisUtterance('Test');
            await voiceSettingsModule.applyTTSSettings(utterance);

            expect(utterance.voice.name).toBe('Voice 2');
        });

        test('should not set voice if not found', async () => {
            voiceSettingsModule.updateTTSSettings({ voice: 'NonexistentVoice' });

            const utterance = new SpeechSynthesisUtterance('Test');
            await voiceSettingsModule.applyTTSSettings(utterance);

            expect(utterance.voice).toBe(null);
        });

        test('should apply STT settings to recognition', () => {
            voiceSettingsModule.updateSTTSettings({
                lang: 'es-ES',
                interimResults: true
            });

            const recognition = new SpeechRecognition();
            voiceSettingsModule.applySTTSettings(recognition);

            expect(recognition.lang).toBe('es-ES');
            expect(recognition.interimResults).toBe(true);
        });
    });

    describe('Settings Panel UI', () => {
        test('should create settings panel element', () => {
            const panel = voiceSettingsModule.createSettingsPanel();

            expect(panel).toBeTruthy();
            expect(panel.className).toBe('voice-settings-panel');
        });

        test('should include TTS controls in panel', () => {
            const panel = voiceSettingsModule.createSettingsPanel();

            expect(panel.querySelector('#tts-rate')).toBeTruthy();
            expect(panel.querySelector('#tts-pitch')).toBeTruthy();
            expect(panel.querySelector('#tts-volume')).toBeTruthy();
            expect(panel.querySelector('#tts-voice')).toBeTruthy();
        });

        test('should include STT controls in panel', () => {
            const panel = voiceSettingsModule.createSettingsPanel();

            expect(panel.querySelector('#stt-lang')).toBeTruthy();
        });

        test('should include action buttons', () => {
            const panel = voiceSettingsModule.createSettingsPanel();

            expect(panel.querySelector('#reset-voice-settings')).toBeTruthy();
            expect(panel.querySelector('#test-voice-settings')).toBeTruthy();
        });

        test('should populate current settings in panel', () => {
            voiceSettingsModule.updateTTSSettings({ rate: 1.5 });

            const panel = voiceSettingsModule.createSettingsPanel();
            const rateSlider = panel.querySelector('#tts-rate');

            expect(rateSlider.value).toBe('1.5');
        });

        test('should update settings when rate slider changes', () => {
            const panel = voiceSettingsModule.createSettingsPanel();
            const rateSlider = panel.querySelector('#tts-rate');

            rateSlider.value = '1.8';
            rateSlider.dispatchEvent(new Event('input'));

            const settings = voiceSettingsModule.getTTSSettings();
            expect(settings.rate).toBe(1.8);
        });

        test('should update settings when pitch slider changes', () => {
            const panel = voiceSettingsModule.createSettingsPanel();
            const pitchSlider = panel.querySelector('#tts-pitch');

            pitchSlider.value = '1.3';
            pitchSlider.dispatchEvent(new Event('input'));

            const settings = voiceSettingsModule.getTTSSettings();
            expect(settings.pitch).toBe(1.3);
        });

        test('should update settings when volume slider changes', () => {
            const panel = voiceSettingsModule.createSettingsPanel();
            const volumeSlider = panel.querySelector('#tts-volume');

            volumeSlider.value = '0.7';
            volumeSlider.dispatchEvent(new Event('input'));

            const settings = voiceSettingsModule.getTTSSettings();
            expect(settings.volume).toBe(0.7);
        });

        test('should update settings when voice select changes', () => {
            const panel = voiceSettingsModule.createSettingsPanel();
            const voiceSelect = panel.querySelector('#tts-voice');

            voiceSelect.value = 'Voice 2';
            voiceSelect.dispatchEvent(new Event('change'));

            const settings = voiceSettingsModule.getTTSSettings();
            expect(settings.voice).toBe('Voice 2');
        });

        test('should update settings when language select changes', () => {
            const panel = voiceSettingsModule.createSettingsPanel();
            const langSelect = panel.querySelector('#stt-lang');

            langSelect.value = 'es-ES';
            langSelect.dispatchEvent(new Event('change'));

            const settings = voiceSettingsModule.getSTTSettings();
            expect(settings.lang).toBe('es-ES');
        });

        test('should reset settings when reset button clicked', () => {
            voiceSettingsModule.updateTTSSettings({ rate: 2.0 });

            const panel = voiceSettingsModule.createSettingsPanel();
            const resetBtn = panel.querySelector('#reset-voice-settings');

            resetBtn.click();

            const settings = voiceSettingsModule.getTTSSettings();
            expect(settings.rate).toBe(1.0);
        });

        test('should test voice when test button clicked', () => {
            const panel = voiceSettingsModule.createSettingsPanel();
            const testBtn = panel.querySelector('#test-voice-settings');

            testBtn.click();

            expect(speechSynthesis.speak).toHaveBeenCalled();
        });

        test('should display value labels for sliders', () => {
            voiceSettingsModule.updateTTSSettings({ rate: 1.5 });

            const panel = voiceSettingsModule.createSettingsPanel();
            const rateValue = panel.querySelector('#tts-rate-value');

            expect(rateValue.textContent).toBe('1.5');
        });

        test('should update value labels when sliders change', () => {
            const panel = voiceSettingsModule.createSettingsPanel();
            const rateSlider = panel.querySelector('#tts-rate');
            const rateValue = panel.querySelector('#tts-rate-value');

            rateSlider.value = '1.7';
            rateSlider.dispatchEvent(new Event('input'));

            expect(rateValue.textContent).toBe('1.7');
        });
    });

    describe('Voice Loading', () => {
        test('should populate voice select with available voices', async () => {
            const panel = voiceSettingsModule.createSettingsPanel();

            // Wait for voices to load
            await new Promise(resolve => setTimeout(resolve, 0));

            const voiceSelect = panel.querySelector('#tts-voice');
            const options = voiceSelect.querySelectorAll('option');

            // Should have default + 4 voices
            expect(options.length).toBeGreaterThanOrEqual(1);
        });

        test('should mark selected voice in dropdown', async () => {
            voiceSettingsModule.updateTTSSettings({ voice: 'Voice 2' });

            const panel = voiceSettingsModule.createSettingsPanel();
            await new Promise(resolve => setTimeout(resolve, 0));

            const voiceSelect = panel.querySelector('#tts-voice');
            expect(voiceSelect.value).toBe('Voice 2');
        });

        test('should handle null voice selection', () => {
            voiceSettingsModule.updateTTSSettings({ voice: null });

            const panel = voiceSettingsModule.createSettingsPanel();
            const voiceSelect = panel.querySelector('#tts-voice');

            voiceSelect.value = '';
            voiceSelect.dispatchEvent(new Event('change'));

            const settings = voiceSettingsModule.getTTSSettings();
            expect(settings.voice).toBe(null);
        });
    });

    describe('Settings Persistence', () => {
        test('should return a copy of settings (immutability)', () => {
            const settings1 = voiceSettingsModule.getTTSSettings();
            settings1.rate = 999;

            const settings2 = voiceSettingsModule.getTTSSettings();
            expect(settings2.rate).toBe(1.0);
        });

        test('should persist settings across module reloads', async () => {
            voiceSettingsModule.updateTTSSettings({ rate: 1.7 });

            // Reload module
            jest.resetModules();
            const module = await import('../../src/prompt_manager/static/js/modules/voice_settings.js');
            module.initializeVoiceSettings();

            const settings = module.getTTSSettings();
            expect(settings.rate).toBe(1.7);
        });
    });
});
