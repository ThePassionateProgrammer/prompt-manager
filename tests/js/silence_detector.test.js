import { describe, it, expect, beforeEach, jest } from '@jest/globals';
import { SilenceDetector } from '../../src/prompt_manager/static/js/modules/silence_detector.js';
import * as Config from '../../src/prompt_manager/static/js/modules/config.js';

describe('SilenceDetector', () => {
    let detector;

    beforeEach(() => {
        detector = new SilenceDetector();
    });

    describe('Constructor', () => {
        it('should create a SilenceDetector instance', () => {
            expect(detector).toBeInstanceOf(SilenceDetector);
        });

        it('should use default silence threshold from config', () => {
            expect(detector.getSilenceThreshold()).toBe(Config.getSilenceThreshold());
        });

        it('should allow custom silence threshold', () => {
            const customDetector = new SilenceDetector({ silenceThreshold: 5000 });
            expect(customDetector.getSilenceThreshold()).toBe(5000);
        });

        it('should initialize with no last speech time', () => {
            expect(detector.lastSpeechTime).toBeNull();
        });

        it('should initialize as not silent', () => {
            expect(detector.isSilent()).toBe(false);
        });
    });

    describe('onSpeechStart', () => {
        it('should record timestamp when speech starts', () => {
            const timestamp = Date.now();
            detector.onSpeechStart(timestamp);
            expect(detector.lastSpeechTime).toBe(timestamp);
        });

        it('should use current time if no timestamp provided', () => {
            const before = Date.now();
            detector.onSpeechStart();
            const after = Date.now();
            expect(detector.lastSpeechTime).toBeGreaterThanOrEqual(before);
            expect(detector.lastSpeechTime).toBeLessThanOrEqual(after);
        });

        it('should update timestamp on subsequent calls', () => {
            detector.onSpeechStart(1000);
            expect(detector.lastSpeechTime).toBe(1000);
            detector.onSpeechStart(2000);
            expect(detector.lastSpeechTime).toBe(2000);
        });
    });

    describe('onSpeechEnd', () => {
        it('should record timestamp when speech ends', () => {
            const timestamp = Date.now();
            detector.onSpeechEnd(timestamp);
            expect(detector.lastSpeechTime).toBe(timestamp);
        });

        it('should use current time if no timestamp provided', () => {
            const before = Date.now();
            detector.onSpeechEnd();
            const after = Date.now();
            expect(detector.lastSpeechTime).toBeGreaterThanOrEqual(before);
            expect(detector.lastSpeechTime).toBeLessThanOrEqual(after);
        });
    });

    describe('isSilent', () => {
        it('should return false if no speech has occurred', () => {
            expect(detector.isSilent()).toBe(false);
        });

        it('should return false immediately after speech ends', () => {
            const now = Date.now();
            detector.onSpeechEnd(now);
            expect(detector.isSilent(now)).toBe(false);
        });

        it('should return false before threshold is exceeded', () => {
            const startTime = 1000;
            detector.onSpeechEnd(startTime);
            expect(detector.isSilent(startTime + 2999)).toBe(false);
        });

        it('should return true when threshold is exceeded', () => {
            const startTime = 1000;
            detector.onSpeechEnd(startTime);
            expect(detector.isSilent(startTime + 3000)).toBe(true);
        });

        it('should return true when well past threshold', () => {
            const startTime = 1000;
            detector.onSpeechEnd(startTime);
            expect(detector.isSilent(startTime + 10000)).toBe(true);
        });

        it('should use current time if no timestamp provided', () => {
            // Set speech end to 5 seconds ago
            detector.onSpeechEnd(Date.now() - 5000);
            expect(detector.isSilent()).toBe(true);
        });

        it('should reset when speech starts again', () => {
            const startTime = 1000;
            detector.onSpeechEnd(startTime);
            expect(detector.isSilent(startTime + 3000)).toBe(true);

            detector.onSpeechStart(startTime + 3100);
            expect(detector.isSilent(startTime + 3100)).toBe(false);
        });

        it('should handle custom silence threshold', () => {
            const customDetector = new SilenceDetector({ silenceThreshold: 5000 });
            const startTime = 1000;
            customDetector.onSpeechEnd(startTime);

            expect(customDetector.isSilent(startTime + 4999)).toBe(false);
            expect(customDetector.isSilent(startTime + 5000)).toBe(true);
        });
    });

    describe('getSilenceDuration', () => {
        it('should return 0 if no speech has occurred', () => {
            expect(detector.getSilenceDuration()).toBe(0);
        });

        it('should return 0 immediately after speech ends', () => {
            const now = Date.now();
            detector.onSpeechEnd(now);
            expect(detector.getSilenceDuration(now)).toBe(0);
        });

        it('should return elapsed time since speech ended', () => {
            const startTime = 1000;
            detector.onSpeechEnd(startTime);
            expect(detector.getSilenceDuration(startTime + 2500)).toBe(2500);
        });

        it('should use current time if no timestamp provided', () => {
            detector.onSpeechEnd(Date.now() - 2500);
            const duration = detector.getSilenceDuration();
            expect(duration).toBeGreaterThanOrEqual(2500);
            expect(duration).toBeLessThan(2600);
        });

        it('should return 0 after speech starts again', () => {
            const startTime = 1000;
            detector.onSpeechEnd(startTime);
            detector.onSpeechStart(startTime + 2000);
            expect(detector.getSilenceDuration(startTime + 3000)).toBe(0);
        });
    });

    describe('reset', () => {
        it('should clear last speech time', () => {
            detector.onSpeechEnd(1000);
            expect(detector.lastSpeechTime).not.toBeNull();
            detector.reset();
            expect(detector.lastSpeechTime).toBeNull();
        });

        it('should make isSilent return false after reset', () => {
            detector.onSpeechEnd(1000);
            expect(detector.isSilent(5000)).toBe(true);
            detector.reset();
            expect(detector.isSilent(5000)).toBe(false);
        });

        it('should make getSilenceDuration return 0 after reset', () => {
            detector.onSpeechEnd(1000);
            expect(detector.getSilenceDuration(5000)).toBeGreaterThan(0);
            detector.reset();
            expect(detector.getSilenceDuration(5000)).toBe(0);
        });
    });

    describe('Edge Cases', () => {
        it('should handle timestamp of 0', () => {
            detector.onSpeechEnd(0);
            expect(detector.isSilent(3000)).toBe(true);
        });

        it('should handle very large timestamps', () => {
            const largeTime = Number.MAX_SAFE_INTEGER - 10000;
            detector.onSpeechEnd(largeTime);
            expect(detector.isSilent(largeTime + 3000)).toBe(true);
        });

        it('should handle negative silence duration gracefully', () => {
            // This shouldn't happen in practice, but let's be defensive
            detector.onSpeechEnd(5000);
            expect(detector.getSilenceDuration(4000)).toBe(0);
        });
    });
});
