/**
 * Unit tests for the Conversation State Indicator Module
 *
 * Tests state visualization, transitions, and accessibility features.
 */

import { describe, test, expect, jest, beforeEach } from '@jest/globals';

let stateIndicatorModule;
let mockConversationMode;

beforeEach(async () => {
    // Reset DOM
    document.body.innerHTML = '';

    // Create a mock conversation mode button for insertion point
    const conversationBtn = document.createElement('button');
    conversationBtn.id = 'conversation-mode-btn';
    const container = document.createElement('div');
    container.appendChild(conversationBtn);
    document.body.appendChild(container);

    // Mock conversation mode
    mockConversationMode = {
        state: 'IDLE',
        isActive: false
    };

    // Clear module cache and re-import
    jest.resetModules();
    stateIndicatorModule = await import('../../src/prompt_manager/static/js/modules/conversation_state_indicator.js');

    // Initialize with mock dependencies
    stateIndicatorModule.initializeStateIndicator({
        conversationMode: mockConversationMode
    });
});

describe('Conversation State Indicator Module', () => {
    describe('Initialization', () => {
        test('should create indicator element on initialization', () => {
            const indicator = document.getElementById('conversation-state-indicator');
            expect(indicator).toBeTruthy();
        });

        test('should create indicator with icon and label', () => {
            const indicator = document.getElementById('conversation-state-indicator');
            const icon = indicator.querySelector('.state-icon');
            const label = indicator.querySelector('.state-label');

            expect(icon).toBeTruthy();
            expect(label).toBeTruthy();
        });

        test('should start hidden in IDLE state', () => {
            const indicator = document.getElementById('conversation-state-indicator');
            expect(indicator.classList.contains('hidden')).toBe(true);
        });

        test('should have accessibility attributes', () => {
            const indicator = document.getElementById('conversation-state-indicator');
            expect(indicator.getAttribute('role')).toBe('status');
            expect(indicator.getAttribute('aria-live')).toBe('polite');
        });

        test('should insert indicator before conversation mode button', () => {
            const indicator = document.getElementById('conversation-state-indicator');
            const conversationBtn = document.getElementById('conversation-mode-btn');

            expect(indicator.nextElementSibling).toBe(conversationBtn);
        });
    });

    describe('State Updates', () => {
        test('should update to LISTENING state', () => {
            stateIndicatorModule.updateState('LISTENING');

            const indicator = document.getElementById('conversation-state-indicator');
            expect(indicator.classList.contains('state-listening')).toBe(true);
            expect(indicator.classList.contains('hidden')).toBe(false);

            const icon = indicator.querySelector('.state-icon');
            const label = indicator.querySelector('.state-label');
            expect(icon.textContent).toBe('🎤');
            expect(label.textContent).toBe('Listening...');
        });

        test('should update to PAUSED state', () => {
            stateIndicatorModule.updateState('PAUSED');

            const indicator = document.getElementById('conversation-state-indicator');
            expect(indicator.classList.contains('state-paused')).toBe(true);

            const icon = indicator.querySelector('.state-icon');
            const label = indicator.querySelector('.state-label');
            expect(icon.textContent).toBe('⏸️');
            expect(label.textContent).toBe('Paused');
        });

        test('should update to SENDING state', () => {
            stateIndicatorModule.updateState('SENDING');

            const indicator = document.getElementById('conversation-state-indicator');
            expect(indicator.classList.contains('state-sending')).toBe(true);

            const icon = indicator.querySelector('.state-icon');
            const label = indicator.querySelector('.state-label');
            expect(icon.textContent).toBe('📤');
            expect(label.textContent).toBe('Sending...');
        });

        test('should update to PLAYING state', () => {
            stateIndicatorModule.updateState('PLAYING');

            const indicator = document.getElementById('conversation-state-indicator');
            expect(indicator.classList.contains('state-playing')).toBe(true);

            const icon = indicator.querySelector('.state-icon');
            const label = indicator.querySelector('.state-label');
            expect(icon.textContent).toBe('🔊');
            expect(label.textContent).toBe('Playing response...');
        });

        test('should hide indicator in IDLE state', () => {
            // First show it
            stateIndicatorModule.updateState('LISTENING');
            let indicator = document.getElementById('conversation-state-indicator');
            expect(indicator.classList.contains('hidden')).toBe(false);

            // Then go to IDLE
            stateIndicatorModule.updateState('IDLE');
            indicator = document.getElementById('conversation-state-indicator');
            expect(indicator.classList.contains('hidden')).toBe(true);
        });

        test('should update aria-label when state changes', () => {
            stateIndicatorModule.updateState('LISTENING');

            const indicator = document.getElementById('conversation-state-indicator');
            expect(indicator.getAttribute('aria-label')).toBe('Conversation mode: Listening...');
        });

        test('should handle unknown state gracefully', () => {
            stateIndicatorModule.updateState('UNKNOWN_STATE');

            const indicator = document.getElementById('conversation-state-indicator');
            // Should default to IDLE config
            expect(indicator.classList.contains('state-idle')).toBe(true);
        });
    });

    describe('State Transitions', () => {
        test('should transition from IDLE to LISTENING', () => {
            stateIndicatorModule.updateState('IDLE');
            stateIndicatorModule.updateState('LISTENING');

            const indicator = document.getElementById('conversation-state-indicator');
            expect(indicator.classList.contains('state-listening')).toBe(true);
            expect(indicator.classList.contains('hidden')).toBe(false);
        });

        test('should transition from LISTENING to PAUSED', () => {
            stateIndicatorModule.updateState('LISTENING');
            stateIndicatorModule.updateState('PAUSED');

            const indicator = document.getElementById('conversation-state-indicator');
            expect(indicator.classList.contains('state-paused')).toBe(true);
            expect(indicator.classList.contains('state-listening')).toBe(false);
        });

        test('should transition from LISTENING to SENDING', () => {
            stateIndicatorModule.updateState('LISTENING');
            stateIndicatorModule.updateState('SENDING');

            const indicator = document.getElementById('conversation-state-indicator');
            expect(indicator.classList.contains('state-sending')).toBe(true);
        });

        test('should transition from SENDING to PLAYING', () => {
            stateIndicatorModule.updateState('SENDING');
            stateIndicatorModule.updateState('PLAYING');

            const indicator = document.getElementById('conversation-state-indicator');
            expect(indicator.classList.contains('state-playing')).toBe(true);
        });

        test('should transition from PLAYING to LISTENING', () => {
            stateIndicatorModule.updateState('PLAYING');
            stateIndicatorModule.updateState('LISTENING');

            const indicator = document.getElementById('conversation-state-indicator');
            expect(indicator.classList.contains('state-listening')).toBe(true);
        });

        test('should transition from any state to IDLE', () => {
            const states = ['LISTENING', 'PAUSED', 'SENDING', 'PLAYING'];

            states.forEach(state => {
                stateIndicatorModule.updateState(state);
                stateIndicatorModule.updateState('IDLE');

                const indicator = document.getElementById('conversation-state-indicator');
                expect(indicator.classList.contains('hidden')).toBe(true);
            });
        });
    });

    describe('Pulse Animation', () => {
        test('should add pulse class when showPulse called', () => {
            stateIndicatorModule.updateState('LISTENING');
            stateIndicatorModule.showPulse();

            const indicator = document.getElementById('conversation-state-indicator');
            expect(indicator.classList.contains('pulse')).toBe(true);
        });

        test('should remove pulse class after animation', (done) => {
            stateIndicatorModule.updateState('LISTENING');
            stateIndicatorModule.showPulse();

            const indicator = document.getElementById('conversation-state-indicator');
            expect(indicator.classList.contains('pulse')).toBe(true);

            // Pulse should be removed after 600ms
            setTimeout(() => {
                expect(indicator.classList.contains('pulse')).toBe(false);
                done();
            }, 700);
        });

        test('should handle pulse when indicator not initialized', () => {
            stateIndicatorModule.destroyIndicator();

            // Should not throw error
            expect(() => stateIndicatorModule.showPulse()).not.toThrow();
        });
    });

    describe('Destroy Indicator', () => {
        test('should remove indicator from DOM', () => {
            let indicator = document.getElementById('conversation-state-indicator');
            expect(indicator).toBeTruthy();

            stateIndicatorModule.destroyIndicator();

            indicator = document.getElementById('conversation-state-indicator');
            expect(indicator).toBeFalsy();
        });

        test('should handle destroy when already destroyed', () => {
            stateIndicatorModule.destroyIndicator();

            // Should not throw error on second destroy
            expect(() => stateIndicatorModule.destroyIndicator()).not.toThrow();
        });
    });

    describe('Error Handling', () => {
        test('should handle updateState when indicator not initialized', () => {
            stateIndicatorModule.destroyIndicator();

            const warnSpy = jest.spyOn(console, 'warn').mockImplementation();
            stateIndicatorModule.updateState('LISTENING');

            expect(warnSpy).toHaveBeenCalledWith('State indicator not initialized');
            warnSpy.mockRestore();
        });

        test('should create indicator even if conversation button not found', async () => {
            // Remove conversation button
            document.getElementById('conversation-mode-btn').remove();

            // Re-initialize
            jest.resetModules();
            const module = await import('../../src/prompt_manager/static/js/modules/conversation_state_indicator.js');
            module.initializeStateIndicator({ conversationMode: mockConversationMode });

            // Should create indicator in body as fallback
            const indicator = document.getElementById('conversation-state-indicator');
            expect(indicator).toBeTruthy();
            expect(indicator.parentElement).toBe(document.body);
        });
    });

    describe('State Configuration', () => {
        test('should use correct icon for each state', () => {
            const stateIcons = {
                'LISTENING': '🎤',
                'PAUSED': '⏸️',
                'SENDING': '📤',
                'PLAYING': '🔊',
                'IDLE': ''
            };

            Object.entries(stateIcons).forEach(([state, expectedIcon]) => {
                stateIndicatorModule.updateState(state);
                const indicator = document.getElementById('conversation-state-indicator');
                const icon = indicator.querySelector('.state-icon');
                expect(icon.textContent).toBe(expectedIcon);
            });
        });

        test('should use correct label for each state', () => {
            const stateLabels = {
                'LISTENING': 'Listening...',
                'PAUSED': 'Paused',
                'SENDING': 'Sending...',
                'PLAYING': 'Playing response...',
                'IDLE': 'Inactive'
            };

            Object.entries(stateLabels).forEach(([state, expectedLabel]) => {
                stateIndicatorModule.updateState(state);
                const indicator = document.getElementById('conversation-state-indicator');
                const label = indicator.querySelector('.state-label');
                expect(label.textContent).toBe(expectedLabel);
            });
        });

        test('should use correct CSS class for each state', () => {
            const stateClasses = {
                'LISTENING': 'state-listening',
                'PAUSED': 'state-paused',
                'SENDING': 'state-sending',
                'PLAYING': 'state-playing',
                'IDLE': 'state-idle'
            };

            Object.entries(stateClasses).forEach(([state, expectedClass]) => {
                stateIndicatorModule.updateState(state);
                const indicator = document.getElementById('conversation-state-indicator');
                expect(indicator.classList.contains(expectedClass)).toBe(true);
            });
        });
    });
});
