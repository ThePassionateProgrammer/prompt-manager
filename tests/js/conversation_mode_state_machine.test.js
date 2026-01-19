import { describe, it, expect, beforeEach, jest } from '@jest/globals';

/**
 * Tests for ConversationMode State Machine
 *
 * Tests the state transitions and business logic of the conversation mode state machine,
 * including both manual mode and hands-free mode behaviors.
 */

describe('ConversationMode State Machine', () => {
    let ConversationModeModule;
    let conversationMode;
    let StateIndicator;

    beforeEach(async () => {
        // Reset modules to get fresh state
        jest.resetModules();

        // Import the module under test
        ConversationModeModule = await import('../../src/prompt_manager/static/js/modules/conversation_mode.js');

        // Create a mock StateIndicator
        const mockStateIndicator = {
            updateState: jest.fn()
        };

        // Initialize dependencies with mock
        ConversationModeModule.initializeDependencies({
            VoiceInteraction: null,
            showNotification: jest.fn(),
            StateIndicator: mockStateIndicator
        });

        StateIndicator = mockStateIndicator;

        // Get the conversation mode state machine
        conversationMode = ConversationModeModule.getConversationMode();

        // Reset state for each test
        conversationMode.isActive = false;
        conversationMode.state = 'IDLE';
        conversationMode.handsFreeModeEnabled = false;
    });

    describe('Initial State', () => {
        it('should start in IDLE state', () => {
            expect(conversationMode.state).toBe('IDLE');
        });

        it('should start as not active', () => {
            expect(conversationMode.isActive).toBe(false);
        });

        it('should start with hands-free mode disabled', () => {
            expect(conversationMode.handsFreeModeEnabled).toBe(false);
        });
    });

    describe('Manual Mode - Basic State Transitions', () => {
        describe('activate()', () => {
            it('should transition from IDLE to LISTENING', () => {
                conversationMode.activate();

                expect(conversationMode.state).toBe('LISTENING');
                expect(conversationMode.isActive).toBe(true);
            });

            it('should update state indicator', () => {
                conversationMode.activate();

                expect(StateIndicator.updateState).toHaveBeenCalledWith('LISTENING');
            });

            it('should throw error if already active', () => {
                conversationMode.activate();

                expect(() => conversationMode.activate()).toThrow('Already active');
            });
        });

        describe('deactivate()', () => {
            it('should transition from LISTENING to IDLE', () => {
                conversationMode.activate();
                conversationMode.deactivate();

                expect(conversationMode.state).toBe('IDLE');
                expect(conversationMode.isActive).toBe(false);
            });

            it('should transition from PAUSED to IDLE', () => {
                conversationMode.activate();
                conversationMode.pauseListening();
                conversationMode.deactivate();

                expect(conversationMode.state).toBe('IDLE');
            });

            it('should transition from SENDING to IDLE', () => {
                conversationMode.activate();
                conversationMode.sendMessage();
                conversationMode.deactivate();

                expect(conversationMode.state).toBe('IDLE');
            });

            it('should transition from PLAYING to IDLE', () => {
                conversationMode.activate();
                conversationMode.sendMessage();
                conversationMode.receiveResponse();
                conversationMode.deactivate();

                expect(conversationMode.state).toBe('IDLE');
            });
        });

        describe('sendMessage()', () => {
            it('should transition from LISTENING to SENDING', () => {
                conversationMode.activate();
                conversationMode.sendMessage();

                expect(conversationMode.state).toBe('SENDING');
            });

            it('should transition from PAUSED to SENDING', () => {
                conversationMode.activate();
                conversationMode.pauseListening();
                conversationMode.sendMessage();

                expect(conversationMode.state).toBe('SENDING');
            });

            it('should throw error if not active', () => {
                expect(() => conversationMode.sendMessage()).toThrow('Not active');
            });

            it('should throw error if already sending', () => {
                conversationMode.activate();
                conversationMode.sendMessage();

                expect(() => conversationMode.sendMessage()).toThrow('Already sending');
            });

            it('should throw error if currently playing', () => {
                conversationMode.activate();
                conversationMode.sendMessage();
                conversationMode.receiveResponse();

                expect(() => conversationMode.sendMessage()).toThrow('Cannot send while playing');
            });
        });

        describe('receiveResponse()', () => {
            it('should transition from SENDING to PLAYING', () => {
                conversationMode.activate();
                conversationMode.sendMessage();
                conversationMode.receiveResponse();

                expect(conversationMode.state).toBe('PLAYING');
            });

            it('should throw error if not in SENDING state', () => {
                conversationMode.activate();

                expect(() => conversationMode.receiveResponse()).toThrow('Not waiting for response');
            });
        });

        describe('finishPlayback()', () => {
            it('should transition from PLAYING to LISTENING', () => {
                conversationMode.activate();
                conversationMode.sendMessage();
                conversationMode.receiveResponse();
                conversationMode.finishPlayback();

                expect(conversationMode.state).toBe('LISTENING');
            });

            it('should throw error if not in PLAYING state', () => {
                conversationMode.activate();

                expect(() => conversationMode.finishPlayback()).toThrow('Not playing');
            });
        });

        describe('pauseListening()', () => {
            it('should transition from LISTENING to PAUSED', () => {
                conversationMode.activate();
                conversationMode.pauseListening();

                expect(conversationMode.state).toBe('PAUSED');
            });

            it('should throw error if not in LISTENING state', () => {
                conversationMode.activate();
                conversationMode.sendMessage();

                expect(() => conversationMode.pauseListening()).toThrow('Cannot pause');
            });
        });

        describe('resumeListening()', () => {
            it('should transition from PAUSED to LISTENING', () => {
                conversationMode.activate();
                conversationMode.pauseListening();
                conversationMode.resumeListening();

                expect(conversationMode.state).toBe('LISTENING');
            });

            it('should throw error if not in PAUSED state', () => {
                conversationMode.activate();

                expect(() => conversationMode.resumeListening()).toThrow('Not paused');
            });
        });

        describe('interruptPlayback()', () => {
            it('should transition from PLAYING to LISTENING', () => {
                conversationMode.activate();
                conversationMode.sendMessage();
                conversationMode.receiveResponse();
                conversationMode.interruptPlayback();

                expect(conversationMode.state).toBe('LISTENING');
            });

            it('should throw error if not in PLAYING state', () => {
                conversationMode.activate();

                expect(() => conversationMode.interruptPlayback()).toThrow('Not playing');
            });
        });
    });

    describe('Hands-Free Mode', () => {
        beforeEach(() => {
            conversationMode.enableHandsFreeMode();
        });

        describe('enableHandsFreeMode()', () => {
            it('should set handsFreeModeEnabled flag', () => {
                expect(conversationMode.handsFreeModeEnabled).toBe(true);
            });
        });

        describe('disableHandsFreeMode()', () => {
            it('should clear handsFreeModeEnabled flag', () => {
                conversationMode.disableHandsFreeMode();

                expect(conversationMode.handsFreeModeEnabled).toBe(false);
            });
        });

        describe('activate() in hands-free mode', () => {
            it('should transition from IDLE to WAKE_LISTENING', () => {
                conversationMode.activate();

                expect(conversationMode.state).toBe('WAKE_LISTENING');
                expect(conversationMode.isActive).toBe(true);
            });

            it('should update state indicator to WAKE_LISTENING', () => {
                conversationMode.activate();

                expect(StateIndicator.updateState).toHaveBeenCalledWith('WAKE_LISTENING');
            });
        });

        describe('onWakeWordDetected()', () => {
            it('should transition from WAKE_LISTENING to LISTENING', () => {
                conversationMode.activate();
                conversationMode.onWakeWordDetected();

                expect(conversationMode.state).toBe('LISTENING');
            });

            it('should not transition if not in WAKE_LISTENING state', () => {
                conversationMode.activate();
                conversationMode.onWakeWordDetected(); // Now in LISTENING
                conversationMode.onWakeWordDetected(); // Should not do anything

                expect(conversationMode.state).toBe('LISTENING');
            });

            it('should log warning if not in WAKE_LISTENING state', () => {
                const consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation();
                conversationMode.activate();
                conversationMode.onWakeWordDetected(); // Now in LISTENING
                conversationMode.onWakeWordDetected(); // Should warn

                expect(consoleWarnSpy).toHaveBeenCalledWith('Wake word detected but not in WAKE_LISTENING state');
                consoleWarnSpy.mockRestore();
            });
        });

        describe('onSleepWordDetected()', () => {
            it('should transition from LISTENING to WAKE_LISTENING', () => {
                conversationMode.activate();
                conversationMode.onWakeWordDetected(); // WAKE_LISTENING → LISTENING
                conversationMode.onSleepWordDetected();

                expect(conversationMode.state).toBe('WAKE_LISTENING');
            });

            it('should not transition if not in LISTENING state', () => {
                conversationMode.activate(); // WAKE_LISTENING
                conversationMode.onSleepWordDetected();

                expect(conversationMode.state).toBe('WAKE_LISTENING');
            });

            it('should log warning if not in LISTENING state', () => {
                const consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation();
                conversationMode.activate(); // WAKE_LISTENING
                conversationMode.onSleepWordDetected();

                expect(consoleWarnSpy).toHaveBeenCalledWith('Sleep word detected but not in LISTENING state');
                consoleWarnSpy.mockRestore();
            });

            it('should not transition if hands-free mode disabled', () => {
                conversationMode.disableHandsFreeMode();
                conversationMode.activate(); // LISTENING (manual mode)
                conversationMode.onSleepWordDetected();

                expect(conversationMode.state).toBe('LISTENING');
            });
        });

        describe('onSilenceDetected()', () => {
            it('should transition from LISTENING to SENDING', () => {
                conversationMode.activate();
                conversationMode.onWakeWordDetected();
                conversationMode.onSilenceDetected();

                expect(conversationMode.state).toBe('SENDING');
            });

            it('should not transition if not in LISTENING state', () => {
                conversationMode.activate(); // WAKE_LISTENING
                conversationMode.onSilenceDetected();

                expect(conversationMode.state).toBe('WAKE_LISTENING');
            });

            it('should not transition if hands-free mode disabled', () => {
                conversationMode.disableHandsFreeMode();
                conversationMode.activate();
                conversationMode.onSilenceDetected();

                expect(conversationMode.state).toBe('LISTENING');
            });
        });

        describe('Complete hands-free conversation flow', () => {
            it('should complete full cycle: IDLE → WAKE_LISTENING → LISTENING → SENDING → PLAYING → LISTENING', () => {
                // Start in IDLE
                expect(conversationMode.state).toBe('IDLE');

                // Activate in hands-free mode
                conversationMode.activate();
                expect(conversationMode.state).toBe('WAKE_LISTENING');

                // Wake word detected
                conversationMode.onWakeWordDetected();
                expect(conversationMode.state).toBe('LISTENING');

                // User stops speaking, silence detected
                conversationMode.onSilenceDetected();
                expect(conversationMode.state).toBe('SENDING');

                // Response received
                conversationMode.receiveResponse();
                expect(conversationMode.state).toBe('PLAYING');

                // Playback finished, auto-loop back to LISTENING
                conversationMode.finishPlayback();
                expect(conversationMode.state).toBe('LISTENING');
            });

            it('should handle sleep word to return to standby', () => {
                conversationMode.activate();
                conversationMode.onWakeWordDetected();
                expect(conversationMode.state).toBe('LISTENING');

                // Sleep word returns to standby
                conversationMode.onSleepWordDetected();
                expect(conversationMode.state).toBe('WAKE_LISTENING');
            });
        });
    });

    describe('Query Methods', () => {
        describe('shouldBeListening()', () => {
            it('should return true when in LISTENING state', () => {
                conversationMode.activate();

                expect(conversationMode.shouldBeListening()).toBe(true);
            });

            it('should return false when in PAUSED state', () => {
                conversationMode.activate();
                conversationMode.pauseListening();

                expect(conversationMode.shouldBeListening()).toBe(false);
            });

            it('should return false when in IDLE state', () => {
                expect(conversationMode.shouldBeListening()).toBe(false);
            });

            it('should return false when in SENDING state', () => {
                conversationMode.activate();
                conversationMode.sendMessage();

                expect(conversationMode.shouldBeListening()).toBe(false);
            });

            it('should return false when in PLAYING state', () => {
                conversationMode.activate();
                conversationMode.sendMessage();
                conversationMode.receiveResponse();

                expect(conversationMode.shouldBeListening()).toBe(false);
            });

            it('should return true when in WAKE_LISTENING state (mic stays on for wake word)', () => {
                conversationMode.enableHandsFreeMode();
                conversationMode.activate();

                // WAKE_LISTENING needs mic to stay active to detect wake word
                expect(conversationMode.shouldBeListening()).toBe(true);
            });
        });

        describe('shouldAutoPlay()', () => {
            it('should return true when active and in SENDING state', () => {
                conversationMode.activate();
                conversationMode.sendMessage();

                expect(conversationMode.shouldAutoPlay()).toBe(true);
            });

            it('should return false when not active', () => {
                expect(conversationMode.shouldAutoPlay()).toBe(false);
            });

            it('should return false when in LISTENING state', () => {
                conversationMode.activate();

                expect(conversationMode.shouldAutoPlay()).toBe(false);
            });
        });

        describe('shouldAutoRestart()', () => {
            it('should return true when active and in PLAYING state', () => {
                conversationMode.activate();
                conversationMode.sendMessage();
                conversationMode.receiveResponse();

                expect(conversationMode.shouldAutoRestart()).toBe(true);
            });

            it('should return false when not active', () => {
                expect(conversationMode.shouldAutoRestart()).toBe(false);
            });

            it('should return false when in SENDING state', () => {
                conversationMode.activate();
                conversationMode.sendMessage();

                expect(conversationMode.shouldAutoRestart()).toBe(false);
            });
        });
    });

    describe('State Indicator Integration', () => {
        it('should update state indicator on each state transition', () => {
            conversationMode.activate();
            expect(StateIndicator.updateState).toHaveBeenCalledWith('LISTENING');

            conversationMode.pauseListening();
            expect(StateIndicator.updateState).toHaveBeenCalledWith('PAUSED');

            conversationMode.resumeListening();
            expect(StateIndicator.updateState).toHaveBeenCalledWith('LISTENING');

            conversationMode.sendMessage();
            expect(StateIndicator.updateState).toHaveBeenCalledWith('SENDING');

            conversationMode.receiveResponse();
            expect(StateIndicator.updateState).toHaveBeenCalledWith('PLAYING');

            conversationMode.finishPlayback();
            expect(StateIndicator.updateState).toHaveBeenCalledWith('LISTENING');

            conversationMode.deactivate();
            expect(StateIndicator.updateState).toHaveBeenCalledWith('IDLE');
        });
    });
});
