/**
 * Integration Test: Silence Detection Timing Accuracy
 *
 * This test verifies that silence detection triggers at the correct time
 * using real timers (not Jest fake timers). This catches timing bugs that
 * unit tests with mocked timers might miss.
 *
 * Why this test is ESSENTIAL:
 * - Unit tests use fake timers (instant execution)
 * - Real browser: setInterval has drift, callbacks have latency
 * - User reported 10s delay instead of 3s - timing regression
 */

import { describe, test, expect, beforeEach } from '@jest/globals';
import { SilenceDetector } from '../../src/prompt_manager/static/js/modules/silence_detector.js';
import { SilenceCheckingService } from '../../src/prompt_manager/static/js/modules/silence_checking_service.js';

describe('Silence Timing Integration Test', () => {
    let silenceDetector;
    let mockConversationMode;
    let service;

    beforeEach(() => {
        silenceDetector = new SilenceDetector({ silenceThreshold: 1000 }); // 1 second for faster test
        mockConversationMode = {
            state: 'LISTENING'
        };
        service = new SilenceCheckingService(silenceDetector, mockConversationMode, {
            checkInterval: 100,
            extendedSilenceThreshold: 5000
        });
    });

    test('should trigger silence callback within acceptable time range', (done) => {
        const startTime = Date.now();
        let callbackFired = false;

        const onSilenceDetected = () => {
            callbackFired = true;
            const elapsed = Date.now() - startTime;

            console.log(`[Timing Test] Silence detected after ${elapsed}ms`);

            // Should fire between 1000ms (threshold) and 1200ms (threshold + check interval + latency)
            expect(elapsed).toBeGreaterThanOrEqual(1000);
            expect(elapsed).toBeLessThan(1500); // Allow 500ms margin for system latency

            service.stop();
            done();
        };

        // Simulate speech ending
        silenceDetector.onSpeechEnd();

        // Start checking for silence
        service.start(onSilenceDetected, () => {});

        // Safety timeout - fail if callback doesn't fire within 3 seconds
        setTimeout(() => {
            if (!callbackFired) {
                service.stop();
                done(new Error('Silence callback never fired'));
            }
        }, 3000);
    }, 5000); // 5 second test timeout

    test('should trigger extended silence callback when normal silence threshold not reached', (done) => {
        // Use a very high normal silence threshold so extended fires first
        const highThresholdDetector = new SilenceDetector({ silenceThreshold: 10000 }); // 10 seconds
        const testService = new SilenceCheckingService(highThresholdDetector, mockConversationMode, {
            checkInterval: 100,
            extendedSilenceThreshold: 2000 // 2 seconds - will fire before normal threshold
        });

        const startTime = Date.now();
        let extendedSilenceFired = false;

        const onExtendedSilence = () => {
            extendedSilenceFired = true;
            const elapsed = Date.now() - startTime;

            console.log(`[Timing Test] Extended silence detected after ${elapsed}ms`);

            // Should fire between 2000ms and 2500ms
            expect(elapsed).toBeGreaterThanOrEqual(2000);
            expect(elapsed).toBeLessThan(2700);

            testService.stop();
            done();
        };

        // Simulate speech ending
        highThresholdDetector.onSpeechEnd();

        // Start checking - extended should fire before normal
        testService.start(() => {
            done(new Error('Normal silence fired instead of extended silence'));
        }, onExtendedSilence);

        // Safety timeout
        setTimeout(() => {
            if (!extendedSilenceFired) {
                testService.stop();
                done(new Error('Extended silence callback never fired'));
            }
        }, 4000);
    }, 5000);

    test('should NOT trigger if state changes from LISTENING', (done) => {
        let callbackFired = false;

        const onSilenceDetected = () => {
            callbackFired = true;
        };

        // Simulate speech ending
        silenceDetector.onSpeechEnd();

        // Start checking
        service.start(onSilenceDetected, () => {});

        // Change state after 500ms (before threshold)
        setTimeout(() => {
            mockConversationMode.state = 'PAUSED';
        }, 500);

        // Verify callback never fired after 2 seconds
        setTimeout(() => {
            expect(callbackFired).toBe(false);
            expect(service.isRunning()).toBe(false);
            done();
        }, 2000);
    }, 3000);

    test('should NOT trigger if speech starts again before threshold', (done) => {
        let callbackFired = false;

        const onSilenceDetected = () => {
            callbackFired = true;
        };

        // Simulate speech ending
        silenceDetector.onSpeechEnd();

        // Start checking
        service.start(onSilenceDetected, () => {});

        // Simulate speech starting again before threshold (at 500ms)
        setTimeout(() => {
            silenceDetector.onSpeechStart();
        }, 500);

        // Verify callback never fired after 2 seconds
        setTimeout(() => {
            expect(callbackFired).toBe(false);
            service.stop();
            done();
        }, 2000);
    }, 3000);
});
