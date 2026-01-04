/**
 * Unit tests for the Error Handler Module
 *
 * Tests error handling, recovery, retry logic, and error classification.
 */

import { describe, test, expect, jest, beforeEach } from '@jest/globals';

let errorHandlerModule;
let mockNotifications;

beforeEach(async () => {
    // Reset DOM
    document.body.innerHTML = '';

    // Mock notifications
    mockNotifications = {
        showNotification: jest.fn()
    };

    // Clear module cache and re-import
    jest.resetModules();
    errorHandlerModule = await import('../../src/prompt_manager/static/js/modules/error_handler.js');

    // Initialize with mock dependencies
    errorHandlerModule.initializeErrorHandler(mockNotifications);
});

describe('Error Handler Module', () => {
    describe('Basic Error Handling', () => {
        test('should handle Error objects', () => {
            const error = new Error('Test error');
            const result = errorHandlerModule.handleError(error, 'Custom message');

            expect(result.handled).toBe(true);
            expect(result.message).toBe('Custom message');
            expect(mockNotifications.showNotification).toHaveBeenCalledWith(
                'Custom message',
                'error',
                5000
            );
        });

        test('should handle string errors', () => {
            const result = errorHandlerModule.handleError('String error', 'Custom message');

            expect(result.handled).toBe(true);
            expect(mockNotifications.showNotification).toHaveBeenCalled();
        });

        test('should generate friendly message if no custom message provided', () => {
            const error = new Error('Failed to fetch');
            const result = errorHandlerModule.handleError(error);

            expect(result.message).toBe('Network error. Please check your connection and try again.');
        });

        test('should log error to console', () => {
            const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
            const error = new Error('Test');

            errorHandlerModule.handleError(error);

            expect(consoleSpy).toHaveBeenCalledWith('Error:', error);
            consoleSpy.mockRestore();
        });
    });

    describe('Error Message Translation', () => {
        test('should translate "Failed to fetch" to friendly message', () => {
            const error = new Error('Failed to fetch');
            const result = errorHandlerModule.handleError(error);

            expect(result.message).toContain('Network error');
        });

        test('should translate "not-allowed" to permission message', () => {
            const error = new Error('not-allowed');
            const result = errorHandlerModule.handleError(error);

            expect(result.message).toContain('Permission denied');
        });

        test('should translate "no-speech" to speech detection message', () => {
            const error = new Error('no-speech');
            const result = errorHandlerModule.handleError(error);

            expect(result.message).toContain('No speech detected');
        });

        test('should translate "TypeError" to generic message', () => {
            const error = new TypeError('Something went wrong');
            const result = errorHandlerModule.handleError(error);

            expect(result.message).toContain('unexpected error');
        });

        test('should use default message for unknown errors', () => {
            const error = new Error('Unknown error type');
            const result = errorHandlerModule.handleError(error);

            expect(result.message).toBe('An error occurred. Please try again.');
        });
    });

    describe('Notification Control', () => {
        test('should not show notification when notify option is false', () => {
            const error = new Error('Test');
            errorHandlerModule.handleError(error, 'Message', { notify: false });

            expect(mockNotifications.showNotification).not.toHaveBeenCalled();
        });

        test('should show notification by default', () => {
            const error = new Error('Test');
            errorHandlerModule.handleError(error, 'Message');

            expect(mockNotifications.showNotification).toHaveBeenCalled();
        });
    });

    describe('Async Function Wrapping', () => {
        test('should wrap async function with error handling', async () => {
            const successFn = jest.fn().mockResolvedValue('success');
            const wrapped = errorHandlerModule.withErrorHandling(successFn);

            const result = await wrapped('arg1', 'arg2');

            expect(result).toBe('success');
            expect(successFn).toHaveBeenCalledWith('arg1', 'arg2');
        });

        test('should handle errors in wrapped async function', async () => {
            const error = new Error('Async error');
            const failingFn = jest.fn().mockRejectedValue(error);
            const wrapped = errorHandlerModule.withErrorHandling(failingFn, 'Custom error');

            await expect(wrapped()).rejects.toThrow('Async error');
            expect(mockNotifications.showNotification).toHaveBeenCalledWith(
                'Custom error',
                'error',
                5000
            );
        });

        test('should preserve function context in wrapped function', async () => {
            const obj = {
                value: 42,
                method: async function() {
                    return this.value;
                }
            };

            const wrapped = errorHandlerModule.withErrorHandling(obj.method);
            const result = await wrapped.call(obj);

            expect(result).toBe(42);
        });
    });

    describe('Safe Execution', () => {
        test('should execute function safely and return result', () => {
            const fn = () => 'success';
            const result = errorHandlerModule.safeExecute(fn);

            expect(result).toBe('success');
        });

        test('should return fallback value on error', () => {
            const fn = () => { throw new Error('Error'); };
            const result = errorHandlerModule.safeExecute(fn, 'fallback');

            expect(result).toBe('fallback');
            expect(mockNotifications.showNotification).toHaveBeenCalled();
        });

        test('should return null as default fallback', () => {
            const fn = () => { throw new Error('Error'); };
            const result = errorHandlerModule.safeExecute(fn);

            expect(result).toBe(null);
        });
    });

    describe('Safe Async Execution', () => {
        test('should execute async function safely and return result', async () => {
            const fn = async () => 'success';
            const result = await errorHandlerModule.safeExecuteAsync(fn);

            expect(result).toBe('success');
        });

        test('should return fallback value on async error', async () => {
            const fn = async () => { throw new Error('Error'); };
            const result = await errorHandlerModule.safeExecuteAsync(fn, 'fallback');

            expect(result).toBe('fallback');
        });
    });

    describe('Retry with Backoff', () => {
        test('should succeed on first try', async () => {
            const fn = jest.fn().mockResolvedValue('success');

            const result = await errorHandlerModule.retryWithBackoff(fn);

            expect(result).toBe('success');
            expect(fn).toHaveBeenCalledTimes(1);
        });

        test('should retry on failure and eventually succeed', async () => {
            const fn = jest.fn()
                .mockRejectedValueOnce(new Error('Fail 1'))
                .mockRejectedValueOnce(new Error('Fail 2'))
                .mockResolvedValue('success');

            const result = await errorHandlerModule.retryWithBackoff(fn, {
                maxRetries: 3,
                delayMs: 10
            });

            expect(result).toBe('success');
            expect(fn).toHaveBeenCalledTimes(3);
        });

        test('should throw error after max retries exceeded', async () => {
            const error = new Error('Persistent error');
            const fn = jest.fn().mockRejectedValue(error);

            await expect(
                errorHandlerModule.retryWithBackoff(fn, {
                    maxRetries: 2,
                    delayMs: 10
                })
            ).rejects.toThrow('Persistent error');

            expect(fn).toHaveBeenCalledTimes(3); // Initial + 2 retries
        });

        test('should use exponential backoff', async () => {
            jest.useFakeTimers();
            const fn = jest.fn().mockRejectedValue(new Error('Error'));

            const promise = errorHandlerModule.retryWithBackoff(fn, {
                maxRetries: 2,
                delayMs: 100,
                backoffMultiplier: 2
            });

            // Fast-forward through delays
            await jest.runAllTimersAsync();

            await expect(promise).rejects.toThrow();

            jest.useRealTimers();
        });

        test('should respect custom backoff multiplier', async () => {
            const fn = jest.fn()
                .mockRejectedValueOnce(new Error('Fail'))
                .mockResolvedValue('success');

            const result = await errorHandlerModule.retryWithBackoff(fn, {
                maxRetries: 2,
                delayMs: 10,
                backoffMultiplier: 3
            });

            expect(result).toBe('success');
        });
    });

    describe('Error Classification', () => {
        test('should identify network errors', () => {
            expect(errorHandlerModule.isNetworkError(new Error('Failed to fetch'))).toBe(true);
            expect(errorHandlerModule.isNetworkError(new Error('NetworkError'))).toBe(true);
            expect(errorHandlerModule.isNetworkError(new Error('Network request failed'))).toBe(true);
            expect(errorHandlerModule.isNetworkError(new Error('ECONNREFUSED'))).toBe(true);
            expect(errorHandlerModule.isNetworkError(new Error('ETIMEDOUT'))).toBe(true);
        });

        test('should identify non-network errors', () => {
            expect(errorHandlerModule.isNetworkError(new Error('Syntax error'))).toBe(false);
            expect(errorHandlerModule.isNetworkError(new Error('Permission denied'))).toBe(false);
        });

        test('should identify recoverable errors', () => {
            // Network errors are recoverable
            expect(errorHandlerModule.isRecoverableError(new Error('Failed to fetch'))).toBe(true);

            // 5xx errors are recoverable
            const serverError = new Error('Server error');
            serverError.status = 500;
            expect(errorHandlerModule.isRecoverableError(serverError)).toBe(true);

            // Timeout errors are recoverable
            expect(errorHandlerModule.isRecoverableError(new Error('timeout'))).toBe(true);
        });

        test('should identify non-recoverable errors', () => {
            // 4xx errors are not recoverable
            const clientError = new Error('Bad request');
            clientError.status = 400;
            expect(errorHandlerModule.isRecoverableError(clientError)).toBe(false);

            // Generic errors are not recoverable
            expect(errorHandlerModule.isRecoverableError(new Error('Generic error'))).toBe(false);
        });

        test('should handle string errors in classification', () => {
            expect(errorHandlerModule.isNetworkError('NetworkError')).toBe(true);
            expect(errorHandlerModule.isRecoverableError('timeout')).toBe(true);
        });
    });

    describe('Global Error Handlers', () => {
        test('should catch uncaught errors', () => {
            const error = new Error('Uncaught error');
            const event = new ErrorEvent('error', { error });

            const prevented = !window.dispatchEvent(event);

            // Error should be handled and default prevented
            expect(prevented).toBe(true);
        });

        test('should catch unhandled promise rejections', () => {
            const reason = new Error('Unhandled rejection');
            const event = new PromiseRejectionEvent('unhandledrejection', {
                promise: Promise.reject(reason),
                reason
            });

            const prevented = !window.dispatchEvent(event);

            expect(prevented).toBe(true);
        });
    });
});
