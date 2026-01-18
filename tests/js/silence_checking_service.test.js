import { describe, it, expect, beforeEach, jest } from '@jest/globals';
import { SilenceCheckingService } from '../../src/prompt_manager/static/js/modules/silence_checking_service.js';

/**
 * Tests for SilenceCheckingService
 *
 * Manages the interval-based checking for silence detection in hands-free mode.
 * When silence threshold (10 seconds) is exceeded, triggers auto-send.
 */

describe('SilenceCheckingService', () => {
    let service;
    let mockSilenceDetector;
    let mockConversationMode;
    let onSilenceCallback;

    beforeEach(() => {
        // Mock SilenceDetector
        mockSilenceDetector = {
            isSilent: jest.fn().mockReturnValue(false),
            getSilenceDuration: jest.fn().mockReturnValue(0)
        };

        // Mock ConversationMode
        mockConversationMode = {
            state: 'LISTENING'
        };

        // Callback
        onSilenceCallback = jest.fn();

        // Create service
        service = new SilenceCheckingService(mockSilenceDetector, mockConversationMode);

        // Use fake timers
        jest.useFakeTimers();
    });

    afterEach(() => {
        jest.useRealTimers();
    });

    describe('Constructor', () => {
        it('should create a SilenceCheckingService instance', () => {
            expect(service).toBeInstanceOf(SilenceCheckingService);
        });

        it('should store silence detector', () => {
            expect(service.silenceDetector).toBe(mockSilenceDetector);
        });

        it('should store conversation mode', () => {
            expect(service.conversationMode).toBe(mockConversationMode);
        });

        it('should have default check interval', () => {
            expect(service.CHECK_INTERVAL_MS).toBe(100);
        });

        it('should allow custom check interval', () => {
            const customService = new SilenceCheckingService(
                mockSilenceDetector,
                mockConversationMode,
                { checkInterval: 200 }
            );
            expect(customService.CHECK_INTERVAL_MS).toBe(200);
        });
    });

    describe('start()', () => {
        it('should start checking interval', () => {
            service.start(onSilenceCallback);

            expect(service.isRunning()).toBe(true);
        });

        it('should check silence at regular intervals', () => {
            service.start(onSilenceCallback);

            // Advance time by check interval
            jest.advanceTimersByTime(100);

            expect(mockSilenceDetector.isSilent).toHaveBeenCalled();
        });

        it('should not start multiple intervals', () => {
            service.start(onSilenceCallback);
            service.start(onSilenceCallback);

            expect(service.isRunning()).toBe(true);
            // Should only have one interval running
        });

        it('should call onSilence callback when silence detected', () => {
            mockSilenceDetector.isSilent.mockReturnValue(true);

            service.start(onSilenceCallback);
            jest.advanceTimersByTime(100);

            expect(onSilenceCallback).toHaveBeenCalled();
        });

        it('should stop checking after silence detected', () => {
            mockSilenceDetector.isSilent.mockReturnValue(true);

            service.start(onSilenceCallback);
            jest.advanceTimersByTime(100);

            expect(service.isRunning()).toBe(false);
        });

        it('should stop checking if state changes from LISTENING', () => {
            service.start(onSilenceCallback);

            // Change state
            mockConversationMode.state = 'PAUSED';

            jest.advanceTimersByTime(100);

            expect(service.isRunning()).toBe(false);
        });

        it('should continue checking while in LISTENING state and not silent', () => {
            service.start(onSilenceCallback);

            jest.advanceTimersByTime(100);
            expect(service.isRunning()).toBe(true);

            jest.advanceTimersByTime(100);
            expect(service.isRunning()).toBe(true);
        });
    });

    describe('stop()', () => {
        it('should stop checking interval', () => {
            service.start(onSilenceCallback);
            expect(service.isRunning()).toBe(true);

            service.stop();

            expect(service.isRunning()).toBe(false);
        });

        it('should not throw error if not running', () => {
            expect(() => service.stop()).not.toThrow();
        });

        it('should prevent further checks after stop', () => {
            service.start(onSilenceCallback);
            service.stop();

            mockSilenceDetector.isSilent.mockClear();
            jest.advanceTimersByTime(100);

            expect(mockSilenceDetector.isSilent).not.toHaveBeenCalled();
        });
    });

    describe('isRunning()', () => {
        it('should return false initially', () => {
            expect(service.isRunning()).toBe(false);
        });

        it('should return true when started', () => {
            service.start(onSilenceCallback);

            expect(service.isRunning()).toBe(true);
        });

        it('should return false after stopped', () => {
            service.start(onSilenceCallback);
            service.stop();

            expect(service.isRunning()).toBe(false);
        });
    });

    describe('Edge Cases', () => {
        it('should handle missing callback gracefully', () => {
            service.start(null);

            mockSilenceDetector.isSilent.mockReturnValue(true);

            expect(() => jest.advanceTimersByTime(100)).not.toThrow();
        });

        it('should handle rapid start/stop cycles', () => {
            service.start(onSilenceCallback);
            service.stop();
            service.start(onSilenceCallback);
            service.stop();
            service.start(onSilenceCallback);

            expect(service.isRunning()).toBe(true);
        });
    });
});
