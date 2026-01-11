/**
 * TranscriptProcessor Tests
 *
 * Tests for transcript processing logic that determines how to handle
 * speech recognition results based on conversation state and detected commands.
 */

import { describe, test, expect, beforeEach } from '@jest/globals';
import { TranscriptProcessor } from '../../src/prompt_manager/static/js/modules/transcript_processor.js';

describe('TranscriptProcessor', () => {
    let processor;
    let mockWakeWordDetector;
    let mockVoiceCommandDetector;
    let mockCommandDetector;
    let mockConversationMode;

    beforeEach(() => {
        // Mock wake word detector
        mockWakeWordDetector = {
            detect: (transcript) => {
                if (transcript.toLowerCase() === 'hey amber') {
                    return { matched: true, type: 'wake' };
                }
                if (transcript.toLowerCase() === 'sleep amber') {
                    return { matched: true, type: 'sleep' };
                }
                return { matched: false, type: null };
            }
        };

        // Mock voice command detector
        mockVoiceCommandDetector = {
            detect: (transcript) => {
                if (transcript.toLowerCase().includes('pause')) {
                    return { matched: true, command: 'pause' };
                }
                if (transcript.toLowerCase().includes('resume')) {
                    return { matched: true, command: 'resume' };
                }
                return { matched: false, command: null };
            }
        };

        // Mock command detector
        mockCommandDetector = {
            detect: (transcript) => {
                if (transcript.toLowerCase().includes('ember') && transcript.toLowerCase().includes('repeat')) {
                    return { matched: true, command: 'repeat' };
                }
                if (transcript.toLowerCase().includes('ember') && transcript.toLowerCase().includes('transcribe')) {
                    return { matched: true, command: 'transcribe' };
                }
                return { matched: false, command: null };
            }
        };

        // Mock conversation mode
        mockConversationMode = {
            state: 'LISTENING',
            handsFreeModeEnabled: true
        };

        processor = new TranscriptProcessor({
            wakeWordDetector: mockWakeWordDetector,
            voiceCommandDetector: mockVoiceCommandDetector,
            commandDetector: mockCommandDetector,
            conversationMode: mockConversationMode
        });
    });

    describe('Constructor', () => {
        test('should create instance with all detectors', () => {
            expect(processor).toBeDefined();
        });

        test('should handle null/undefined detectors gracefully', () => {
            const minimalProcessor = new TranscriptProcessor({
                conversationMode: mockConversationMode
            });
            expect(minimalProcessor).toBeDefined();
        });
    });

    describe('Wake Word Detection', () => {
        test('should detect wake word in WAKE_LISTENING state', () => {
            mockConversationMode.state = 'WAKE_LISTENING';
            const result = processor.process('hey amber');

            expect(result.action).toBe('WAKE');
            expect(result.shouldTranscribe).toBe(false);
            expect(result.message).toContain('Listening');
        });

        test('should not detect wake word in LISTENING state', () => {
            mockConversationMode.state = 'LISTENING';
            const result = processor.process('hey amber');

            // Should just transcribe the text, not trigger wake
            expect(result.action).toBe('TRANSCRIBE');
            expect(result.shouldTranscribe).toBe(true);
        });

        test('should not process wake word if hands-free disabled', () => {
            mockConversationMode.handsFreeModeEnabled = false;
            mockConversationMode.state = 'WAKE_LISTENING';
            const result = processor.process('hey amber');

            expect(result.action).toBe('TRANSCRIBE');
        });
    });

    describe('Sleep Word Detection', () => {
        test('should detect sleep word in LISTENING state', () => {
            mockConversationMode.state = 'LISTENING';
            const result = processor.process('sleep amber');

            expect(result.action).toBe('SLEEP');
            expect(result.shouldTranscribe).toBe(false);
            expect(result.message).toContain('Standby');
        });

        test('should not detect sleep word in WAKE_LISTENING state', () => {
            mockConversationMode.state = 'WAKE_LISTENING';
            const result = processor.process('sleep amber');

            // In standby, don't transcribe anything
            expect(result.action).toBe('IGNORE');
            expect(result.shouldTranscribe).toBe(false);
        });
    });

    describe('Voice Commands (Pause/Resume)', () => {
        test('should detect pause command in LISTENING state', () => {
            mockConversationMode.state = 'LISTENING';
            const result = processor.process('amber pause');

            expect(result.action).toBe('PAUSE');
            expect(result.shouldTranscribe).toBe(false);
            expect(result.message).toContain('Paused');
        });

        test('should not trigger pause in PAUSED state', () => {
            mockConversationMode.state = 'PAUSED';
            const result = processor.process('amber pause');

            expect(result.action).toBe('IGNORE');
        });

        test('should detect resume command in PAUSED state', () => {
            mockConversationMode.state = 'PAUSED';
            const result = processor.process('amber resume');

            expect(result.action).toBe('RESUME');
            expect(result.shouldTranscribe).toBe(false);
            expect(result.message).toContain('Resumed');
        });

        test('should not trigger resume in LISTENING state', () => {
            mockConversationMode.state = 'LISTENING';
            const result = processor.process('amber resume');

            // Should just transcribe
            expect(result.action).toBe('TRANSCRIBE');
            expect(result.shouldTranscribe).toBe(true);
        });
    });

    describe('Ember Commands', () => {
        test('should detect repeat command in LISTENING state', () => {
            mockConversationMode.state = 'LISTENING';
            const result = processor.process('ember repeat that');

            expect(result.action).toBe('REPEAT');
            expect(result.shouldTranscribe).toBe(false);
        });

        test('should detect transcribe command in LISTENING state', () => {
            mockConversationMode.state = 'LISTENING';
            const result = processor.process('ember transcribe this');

            expect(result.action).toBe('TRANSCRIBE_MODE');
            expect(result.shouldTranscribe).toBe(false);
        });

        test('should not trigger commands in PAUSED state', () => {
            mockConversationMode.state = 'PAUSED';
            const result = processor.process('ember repeat that');

            expect(result.action).toBe('IGNORE');
        });
    });

    describe('State-Based Filtering', () => {
        test('should ignore all speech in WAKE_LISTENING state (except wake word)', () => {
            mockConversationMode.state = 'WAKE_LISTENING';
            const result = processor.process('hello world');

            expect(result.action).toBe('IGNORE');
            expect(result.shouldTranscribe).toBe(false);
        });

        test('should ignore all speech in PAUSED state (except resume)', () => {
            mockConversationMode.state = 'PAUSED';
            const result = processor.process('hello world');

            expect(result.action).toBe('IGNORE');
            expect(result.shouldTranscribe).toBe(false);
        });

        test('should transcribe normal speech in LISTENING state', () => {
            mockConversationMode.state = 'LISTENING';
            const result = processor.process('hello world');

            expect(result.action).toBe('TRANSCRIBE');
            expect(result.shouldTranscribe).toBe(true);
        });
    });

    describe('Hands-Free Mode Disabled', () => {
        beforeEach(() => {
            mockConversationMode.handsFreeModeEnabled = false;
        });

        test('should transcribe everything when hands-free disabled', () => {
            const result = processor.process('hey amber');

            expect(result.action).toBe('TRANSCRIBE');
            expect(result.shouldTranscribe).toBe(true);
        });

        test('should not detect wake words when hands-free disabled', () => {
            mockConversationMode.state = 'WAKE_LISTENING';
            const result = processor.process('hey amber');

            expect(result.action).not.toBe('WAKE');
        });
    });

    describe('Priority Order', () => {
        test('should check wake word before other commands', () => {
            mockConversationMode.state = 'WAKE_LISTENING';
            // Wake word must match exactly
            const result = processor.process('hey amber');

            expect(result.action).toBe('WAKE');
        });

        test('should check sleep word before voice commands', () => {
            mockConversationMode.state = 'LISTENING';
            const result = processor.process('sleep amber');

            expect(result.action).toBe('SLEEP');
            expect(result.action).not.toBe('PAUSE');
        });
    });
});
