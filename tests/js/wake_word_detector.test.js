import { describe, it, expect, beforeEach } from '@jest/globals';
import { WakeWordDetector } from '../../src/prompt_manager/static/js/modules/wake_word_detector.js';
import * as Config from '../../src/prompt_manager/static/js/modules/config.js';

describe('WakeWordDetector', () => {
    let detector;

    beforeEach(() => {
        detector = new WakeWordDetector();
    });

    describe('Constructor', () => {
        it('should create a WakeWordDetector instance', () => {
            expect(detector).toBeInstanceOf(WakeWordDetector);
        });

        it('should use default wake word from config', () => {
            expect(detector.wakeWord).toBe(Config.getWakeWord());
        });

        it('should use default sleep word from config', () => {
            expect(detector.sleepWord).toBe(Config.getSleepWord());
        });

        it('should allow custom wake word', () => {
            const customDetector = new WakeWordDetector({ wakeWord: 'hello assistant' });
            expect(customDetector.wakeWord).toBe('hello assistant');
        });

        it('should allow custom sleep word', () => {
            const customDetector = new WakeWordDetector({ sleepWord: 'goodbye assistant' });
            expect(customDetector.sleepWord).toBe('goodbye assistant');
        });

        it('should accept array of wake words', () => {
            const customDetector = new WakeWordDetector({
                wakeWords: ['hey amber', 'hi amber', 'amber']
            });
            expect(customDetector.wakeWords).toEqual(['hey amber', 'hi amber', 'amber']);
        });

        it('should accept array of sleep words', () => {
            const customDetector = new WakeWordDetector({
                sleepWords: ['sleep amber', 'goodbye amber', 'stop']
            });
            expect(customDetector.sleepWords).toEqual(['sleep amber', 'goodbye amber', 'stop']);
        });

        it('should convert single wake word to array internally', () => {
            const customDetector = new WakeWordDetector({ wakeWord: 'hello' });
            expect(Array.isArray(customDetector.wakeWords)).toBe(true);
            expect(customDetector.wakeWords).toContain('hello');
        });

        it('should convert single sleep word to array internally', () => {
            const customDetector = new WakeWordDetector({ sleepWord: 'bye' });
            expect(Array.isArray(customDetector.sleepWords)).toBe(true);
            expect(customDetector.sleepWords).toContain('bye');
        });
    });

    describe('detectWakeWord', () => {
        it('should return true for exact wake word match', () => {
            const result = detector.detectWakeWord('hey amber');
            expect(result).toBe(true);
        });

        it('should return false for non-matching text', () => {
            const result = detector.detectWakeWord('hello there');
            expect(result).toBe(false);
        });

        it('should be case insensitive', () => {
            expect(detector.detectWakeWord('HEY AMBER')).toBe(true);
            expect(detector.detectWakeWord('Hey Amber')).toBe(true);
            expect(detector.detectWakeWord('hey amber')).toBe(true);
        });

        it('should handle leading and trailing whitespace', () => {
            expect(detector.detectWakeWord('  hey amber  ')).toBe(true);
            expect(detector.detectWakeWord('\they amber\n')).toBe(true);
        });

        it('should return false for partial matches', () => {
            expect(detector.detectWakeWord('hey')).toBe(false);
            expect(detector.detectWakeWord('hello')).toBe(false);
        });

        it('should detect multiple wake word variations', () => {
            const multiDetector = new WakeWordDetector({
                wakeWords: ['hey amber', 'hi amber', 'amber']
            });

            expect(multiDetector.detectWakeWord('hey amber')).toBe(true);
            expect(multiDetector.detectWakeWord('hi amber')).toBe(true);
            expect(multiDetector.detectWakeWord('amber')).toBe(true);
            // "hello amber" now matches because it ends with " amber" (a wake word)
            expect(multiDetector.detectWakeWord('hello amber')).toBe(true);
            // But "hello amber time" should not match (wake word not at end)
            expect(multiDetector.detectWakeWord('hello amber time')).toBe(false);
        });

        it('should return true for wake word at end of sentence', () => {
            expect(detector.detectWakeWord('okay hey amber')).toBe(true);
            expect(detector.detectWakeWord('alright, hey amber')).toBe(true);
        });

        it('should return false for wake word at start/middle of sentence', () => {
            expect(detector.detectWakeWord('hey amber said hello')).toBe(false);
            expect(detector.detectWakeWord('I said hey amber yesterday')).toBe(false);
        });

        it('should return false for empty string', () => {
            expect(detector.detectWakeWord('')).toBe(false);
        });

        it('should return false for null or undefined', () => {
            expect(detector.detectWakeWord(null)).toBe(false);
            expect(detector.detectWakeWord(undefined)).toBe(false);
        });

        it('should handle non-string input gracefully', () => {
            expect(detector.detectWakeWord(123)).toBe(false);
            expect(detector.detectWakeWord({})).toBe(false);
            expect(detector.detectWakeWord([])).toBe(false);
        });
    });

    describe('detectSleepWord', () => {
        it('should return true for exact sleep word match', () => {
            const result = detector.detectSleepWord('sleep amber');
            expect(result).toBe(true);
        });

        it('should return false for non-matching text', () => {
            const result = detector.detectSleepWord('goodbye');
            expect(result).toBe(false);
        });

        it('should be case insensitive', () => {
            expect(detector.detectSleepWord('SLEEP AMBER')).toBe(true);
            expect(detector.detectSleepWord('Sleep Amber')).toBe(true);
            expect(detector.detectSleepWord('sleep amber')).toBe(true);
        });

        it('should handle leading and trailing whitespace', () => {
            expect(detector.detectSleepWord('  sleep amber  ')).toBe(true);
            expect(detector.detectSleepWord('\tsleep amber\n')).toBe(true);
        });

        it('should detect multiple sleep word variations', () => {
            const multiDetector = new WakeWordDetector({
                sleepWords: ['sleep amber', 'goodbye amber', 'stop']
            });

            expect(multiDetector.detectSleepWord('sleep amber')).toBe(true);
            expect(multiDetector.detectSleepWord('goodbye amber')).toBe(true);
            expect(multiDetector.detectSleepWord('stop')).toBe(true);
            expect(multiDetector.detectSleepWord('pause amber')).toBe(false);
        });

        it('should return false for partial matches', () => {
            expect(detector.detectSleepWord('sleep')).toBe(false);
            expect(detector.detectSleepWord('amber')).toBe(false);
        });

        it('should return true for sleep word at end of sentence', () => {
            expect(detector.detectSleepWord('thank you sleep amber')).toBe(true);
            expect(detector.detectSleepWord('okay, goodbye amber')).toBe(true);
        });

        it('should return false for sleep word at start/middle of sentence', () => {
            expect(detector.detectSleepWord('sleep amber is what I need')).toBe(false);
            expect(detector.detectSleepWord('I need sleep amber is tired')).toBe(false);
        });

        it('should return false for empty string', () => {
            expect(detector.detectSleepWord('')).toBe(false);
        });

        it('should return false for null or undefined', () => {
            expect(detector.detectSleepWord(null)).toBe(false);
            expect(detector.detectSleepWord(undefined)).toBe(false);
        });
    });

    describe('detect (combined)', () => {
        it('should return wake signal for wake word', () => {
            const result = detector.detect('hey amber');
            expect(result).toEqual({ type: 'wake', matched: true });
        });

        it('should return sleep signal for sleep word', () => {
            const result = detector.detect('sleep amber');
            expect(result).toEqual({ type: 'sleep', matched: true });
        });

        it('should return no match for regular text', () => {
            const result = detector.detect('hello how are you');
            expect(result).toEqual({ type: null, matched: false });
        });

        it('should prioritize sleep word over wake word if both match', () => {
            // Sleep words are checked first because they're typically more specific
            // (e.g., "sleep amber" should match sleep, not wake for just "amber")
            const detector = new WakeWordDetector({
                wakeWord: 'test',
                sleepWord: 'test'
            });
            const result = detector.detect('test');
            expect(result.type).toBe('sleep');
        });
    });

    describe('Edge Cases', () => {
        it('should handle very long transcripts efficiently', () => {
            const longText = 'a '.repeat(10000);
            const result = detector.detect(longText);
            expect(result.matched).toBe(false);
        });

        it('should handle special characters in transcript', () => {
            expect(detector.detect('hey amber!').matched).toBe(false);
            expect(detector.detect('hey amber?').matched).toBe(false);
            expect(detector.detect('hey-amber').matched).toBe(false);
        });
    });
});
