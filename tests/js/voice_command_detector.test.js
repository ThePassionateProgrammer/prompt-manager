import { describe, it, expect, beforeEach } from '@jest/globals';
import { VoiceCommandDetector } from '../../src/prompt_manager/static/js/modules/voice_command_detector.js';

/**
 * Tests for VoiceCommandDetector
 *
 * Detects pause/resume voice commands in transcripts.
 * Similar to WakeWordDetector but for conversation control commands.
 */

describe('VoiceCommandDetector', () => {
    let detector;

    beforeEach(() => {
        detector = new VoiceCommandDetector();
    });

    describe('Constructor', () => {
        it('should create a VoiceCommandDetector instance', () => {
            expect(detector).toBeInstanceOf(VoiceCommandDetector);
        });

        it('should have default pause command variations', () => {
            expect(detector.pauseCommands).toBeDefined();
            expect(detector.pauseCommands.length).toBeGreaterThan(0);
        });

        it('should have default resume command variations', () => {
            expect(detector.resumeCommands).toBeDefined();
            expect(detector.resumeCommands.length).toBeGreaterThan(0);
        });

        it('should allow custom pause commands', () => {
            const customDetector = new VoiceCommandDetector({
                pauseCommands: ['stop listening', 'pause']
            });
            expect(customDetector.pauseCommands).toEqual(['stop listening', 'pause']);
        });

        it('should allow custom resume commands', () => {
            const customDetector = new VoiceCommandDetector({
                resumeCommands: ['continue', 'go']
            });
            expect(customDetector.resumeCommands).toEqual(['continue', 'go']);
        });
    });

    describe('detectPause', () => {
        it('should detect "amber pause"', () => {
            expect(detector.detectPause('amber pause')).toBe(true);
        });

        it('should detect "amber, pause"', () => {
            expect(detector.detectPause('amber, pause')).toBe(true);
        });

        it('should detect "pause amber"', () => {
            expect(detector.detectPause('pause amber')).toBe(true);
        });

        it('should be case insensitive', () => {
            expect(detector.detectPause('AMBER PAUSE')).toBe(true);
            expect(detector.detectPause('Amber Pause')).toBe(true);
            expect(detector.detectPause('amber pause')).toBe(true);
        });

        it('should handle leading and trailing whitespace', () => {
            expect(detector.detectPause('  amber pause  ')).toBe(true);
            expect(detector.detectPause('\tamber pause\n')).toBe(true);
        });

        it('should return false for non-pause commands', () => {
            expect(detector.detectPause('amber resume')).toBe(false);
            expect(detector.detectPause('hello amber')).toBe(false);
            expect(detector.detectPause('pause')).toBe(false);
        });

        it('should return false for empty string', () => {
            expect(detector.detectPause('')).toBe(false);
        });

        it('should return false for null or undefined', () => {
            expect(detector.detectPause(null)).toBe(false);
            expect(detector.detectPause(undefined)).toBe(false);
        });
    });

    describe('detectResume', () => {
        it('should detect "amber resume"', () => {
            expect(detector.detectResume('amber resume')).toBe(true);
        });

        it('should detect "amber, resume"', () => {
            expect(detector.detectResume('amber, resume')).toBe(true);
        });

        it('should detect "resume amber"', () => {
            expect(detector.detectResume('resume amber')).toBe(true);
        });

        it('should be case insensitive', () => {
            expect(detector.detectResume('AMBER RESUME')).toBe(true);
            expect(detector.detectResume('Amber Resume')).toBe(true);
            expect(detector.detectResume('amber resume')).toBe(true);
        });

        it('should handle leading and trailing whitespace', () => {
            expect(detector.detectResume('  amber resume  ')).toBe(true);
            expect(detector.detectResume('\tamber resume\n')).toBe(true);
        });

        it('should return false for non-resume commands', () => {
            expect(detector.detectResume('amber pause')).toBe(false);
            expect(detector.detectResume('hello amber')).toBe(false);
            expect(detector.detectResume('resume')).toBe(false);
        });

        it('should return false for empty string', () => {
            expect(detector.detectResume('')).toBe(false);
        });

        it('should return false for null or undefined', () => {
            expect(detector.detectResume(null)).toBe(false);
            expect(detector.detectResume(undefined)).toBe(false);
        });
    });

    describe('detect (combined)', () => {
        it('should return pause signal for pause command', () => {
            const result = detector.detect('amber pause');
            expect(result).toEqual({ matched: true, command: 'pause' });
        });

        it('should return resume signal for resume command', () => {
            const result = detector.detect('amber resume');
            expect(result).toEqual({ matched: true, command: 'resume' });
        });

        it('should return no match for regular text', () => {
            const result = detector.detect('hello how are you');
            expect(result).toEqual({ matched: false, command: null });
        });

        it('should handle all pause variations', () => {
            expect(detector.detect('amber pause').command).toBe('pause');
            expect(detector.detect('amber, pause').command).toBe('pause');
            expect(detector.detect('pause amber').command).toBe('pause');
        });

        it('should handle all resume variations', () => {
            expect(detector.detect('amber resume').command).toBe('resume');
            expect(detector.detect('amber, resume').command).toBe('resume');
            expect(detector.detect('resume amber').command).toBe('resume');
        });
    });

    describe('Edge Cases', () => {
        it('should handle non-string input gracefully', () => {
            expect(detector.detect(123)).toEqual({ matched: false, command: null });
            expect(detector.detect({})).toEqual({ matched: false, command: null });
            expect(detector.detect([])).toEqual({ matched: false, command: null });
        });

        it('should handle very long transcripts efficiently', () => {
            const longText = 'a '.repeat(10000);
            const result = detector.detect(longText);
            expect(result.matched).toBe(false);
        });

        it('should not match partial commands', () => {
            expect(detector.detect('amber').matched).toBe(false);
            expect(detector.detect('pause').matched).toBe(false);
            expect(detector.detect('resume').matched).toBe(false);
        });

        it('should not match commands as part of larger sentence', () => {
            expect(detector.detect('I told amber pause to wait').matched).toBe(false);
            expect(detector.detect('please amber resume the video').matched).toBe(false);
        });
    });
});
