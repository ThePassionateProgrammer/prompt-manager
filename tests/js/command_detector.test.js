/**
 * Unit tests for CommandDetector
 *
 * Tests detection of command word (Ember) followed by specific commands.
 * This enables "Ember, repeat that" style voice commands.
 */

import { describe, test, expect, beforeEach } from '@jest/globals';
import { CommandDetector } from '../../src/prompt_manager/static/js/modules/command_detector.js';

describe('CommandDetector', () => {
    let detector;

    beforeEach(() => {
        detector = new CommandDetector();
    });

    describe('Constructor', () => {
        test('should create a CommandDetector instance', () => {
            expect(detector).toBeInstanceOf(CommandDetector);
        });

        test('should use default command word from config', () => {
            expect(detector.commandWord).toBe('ember');
        });

        test('should allow custom command word', () => {
            const customDetector = new CommandDetector({ commandWord: 'computer' });
            expect(customDetector.commandWord).toBe('computer');
        });

        test('should normalize command word to lowercase', () => {
            const customDetector = new CommandDetector({ commandWord: 'EMBER' });
            expect(customDetector.commandWord).toBe('ember');
        });
    });

    describe('Command Detection', () => {
        test('should detect "ember repeat that"', () => {
            const result = detector.detect('ember repeat that');
            expect(result.matched).toBe(true);
            expect(result.command).toBe('repeat');
        });

        test('should detect "ember, repeat that" with comma', () => {
            const result = detector.detect('ember, repeat that');
            expect(result.matched).toBe(true);
            expect(result.command).toBe('repeat');
        });

        test('should detect "ember transcribe this"', () => {
            const result = detector.detect('ember transcribe this');
            expect(result.matched).toBe(true);
            expect(result.command).toBe('transcribe');
        });

        test('should be case insensitive', () => {
            expect(detector.detect('EMBER REPEAT THAT').matched).toBe(true);
            expect(detector.detect('Ember Repeat That').matched).toBe(true);
            expect(detector.detect('ember repeat that').matched).toBe(true);
        });

        test('should handle extra whitespace', () => {
            const result = detector.detect('  ember   repeat   that  ');
            expect(result.matched).toBe(true);
            expect(result.command).toBe('repeat');
        });

        test('should return false for command word alone', () => {
            const result = detector.detect('ember');
            expect(result.matched).toBe(false);
            expect(result.command).toBe(null);
        });

        test('should return false for non-command after command word', () => {
            const result = detector.detect('ember hello there');
            expect(result.matched).toBe(false);
            expect(result.command).toBe(null);
        });

        test('should return false for command word in middle of sentence', () => {
            const result = detector.detect('I said ember repeat that yesterday');
            expect(result.matched).toBe(false);
        });

        test('should return false for empty string', () => {
            const result = detector.detect('');
            expect(result.matched).toBe(false);
            expect(result.command).toBe(null);
        });

        test('should return false for null or undefined', () => {
            expect(detector.detect(null).matched).toBe(false);
            expect(detector.detect(undefined).matched).toBe(false);
        });

        test('should handle non-string input gracefully', () => {
            expect(detector.detect(123).matched).toBe(false);
            expect(detector.detect({}).matched).toBe(false);
            expect(detector.detect([]).matched).toBe(false);
        });
    });

    describe('Supported Commands', () => {
        test('should list supported commands', () => {
            const commands = detector.getSupportedCommands();
            expect(commands).toContain('repeat');
            expect(commands).toContain('transcribe');
        });

        test('should check if command is supported', () => {
            expect(detector.isCommandSupported('repeat')).toBe(true);
            expect(detector.isCommandSupported('transcribe')).toBe(true);
            expect(detector.isCommandSupported('invalid')).toBe(false);
        });
    });

    describe('Command Variations', () => {
        test('should detect "repeat" with various suffixes', () => {
            expect(detector.detect('ember repeat that').command).toBe('repeat');
            expect(detector.detect('ember repeat').command).toBe('repeat');
        });

        test('should detect "transcribe" with various suffixes', () => {
            expect(detector.detect('ember transcribe this').command).toBe('transcribe');
            expect(detector.detect('ember transcribe').command).toBe('transcribe');
        });
    });

    describe('Edge Cases', () => {
        test('should handle very long transcripts', () => {
            const longText = 'a '.repeat(1000) + 'ember repeat that';
            const result = detector.detect(longText);
            expect(result.matched).toBe(false); // Should be exact match at start
        });

        test('should handle special characters in transcript', () => {
            const result = detector.detect('ember, repeat that!');
            expect(result.matched).toBe(true);
        });

        test('should handle multiple commas', () => {
            const result = detector.detect('ember,, repeat that');
            expect(result.matched).toBe(true);
        });
    });

    describe('Custom Command Configuration', () => {
        test('should allow custom command definitions', () => {
            const customDetector = new CommandDetector({
                commands: {
                    'pause': ['pause', 'stop'],
                    'resume': ['resume', 'continue', 'go']
                }
            });

            expect(customDetector.detect('ember pause').command).toBe('pause');
            expect(customDetector.detect('ember stop').command).toBe('pause');
            expect(customDetector.detect('ember resume').command).toBe('resume');
            expect(customDetector.detect('ember go').command).toBe('resume');
        });
    });
});
