/**
 * Error Handler Module
 *
 * Centralized error handling and recovery for the application.
 * Provides graceful degradation and user-friendly error messages.
 *
 * Features:
 * - Global error catching
 * - User-friendly error messages
 * - Error logging
 * - Automatic recovery attempts
 * - Integration with notification system
 */

let notificationModule = null;

/**
 * Initialize error handler with dependencies.
 *
 * @param {Object} deps - Dependencies
 * @param {Function} deps.showNotification - Notification function
 */
export function initializeErrorHandler(deps) {
    notificationModule = deps;

    // Set up global error handlers
    setupGlobalErrorHandlers();
}

/**
 * Set up global error handlers for unhandled errors and promise rejections.
 */
function setupGlobalErrorHandlers() {
    // Handle uncaught errors
    window.addEventListener('error', (event) => {
        console.error('Uncaught error:', event.error);
        handleError(event.error, 'An unexpected error occurred');
        // Prevent default browser error handling
        event.preventDefault();
    });

    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
        console.error('Unhandled promise rejection:', event.reason);
        handleError(event.reason, 'An unexpected error occurred');
        // Prevent default browser error handling
        event.preventDefault();
    });
}

/**
 * Handle an error with logging and user notification.
 *
 * @param {Error|string} error - The error object or message
 * @param {string} userMessage - User-friendly message to display
 * @param {Object} options - Additional options
 * @param {boolean} options.notify - Whether to show notification (default: true)
 * @param {boolean} options.logToServer - Whether to log to server (default: false)
 */
export function handleError(error, userMessage = null, options = {}) {
    const { notify = true, logToServer = false } = options;

    // Log error to console
    console.error('Error:', error);

    // Extract error message
    const errorMessage = error instanceof Error ? error.message : String(error);

    // Determine user-friendly message
    const displayMessage = userMessage || getFriendlyErrorMessage(errorMessage);

    // Show notification if requested
    if (notify && notificationModule && notificationModule.showNotification) {
        notificationModule.showNotification(displayMessage, 'error', 5000);
    }

    // Log to server if requested (implement when backend logging is available)
    if (logToServer) {
        logErrorToServer(error, errorMessage);
    }

    return { handled: true, message: displayMessage };
}

/**
 * Convert technical error messages to user-friendly ones.
 *
 * @param {string} errorMessage - Technical error message
 * @returns {string} User-friendly error message
 */
function getFriendlyErrorMessage(errorMessage) {
    const errorMap = {
        'Failed to fetch': 'Network error. Please check your connection and try again.',
        'NetworkError': 'Network error. Please check your connection and try again.',
        'TypeError': 'An unexpected error occurred. Please refresh the page.',
        'not-allowed': 'Permission denied. Please grant the necessary permissions.',
        'no-speech': 'No speech detected. Please try again.',
        'audio-capture': 'Microphone access denied. Please enable microphone permissions.',
        'aborted': 'The operation was cancelled.',
    };

    // Check if error message contains any known error patterns
    for (const [pattern, friendlyMessage] of Object.entries(errorMap)) {
        if (errorMessage.toLowerCase().includes(pattern.toLowerCase())) {
            return friendlyMessage;
        }
    }

    // Default message for unknown errors
    return 'An error occurred. Please try again.';
}

/**
 * Log error to server for monitoring (placeholder for future implementation).
 *
 * @param {Error|string} error - The error
 * @param {string} errorMessage - Error message
 */
function logErrorToServer(error, errorMessage) {
    // TODO: Implement server-side error logging
    // This could send errors to a logging endpoint for monitoring
    console.log('Would log to server:', {
        message: errorMessage,
        stack: error instanceof Error ? error.stack : null,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href
    });
}

/**
 * Wrap an async function with error handling.
 *
 * @param {Function} fn - Async function to wrap
 * @param {string} errorMessage - Custom error message for user
 * @returns {Function} Wrapped function with error handling
 */
export function withErrorHandling(fn, errorMessage = null) {
    return async function(...args) {
        try {
            return await fn.apply(this, args);
        } catch (error) {
            handleError(error, errorMessage);
            throw error; // Re-throw for caller to handle if needed
        }
    };
}

/**
 * Safely execute a function with error handling.
 *
 * @param {Function} fn - Function to execute
 * @param {*} fallbackValue - Value to return if error occurs
 * @param {string} errorMessage - Custom error message
 * @returns {*} Function result or fallback value
 */
export function safeExecute(fn, fallbackValue = null, errorMessage = null) {
    try {
        return fn();
    } catch (error) {
        handleError(error, errorMessage);
        return fallbackValue;
    }
}

/**
 * Safely execute an async function with error handling.
 *
 * @param {Function} fn - Async function to execute
 * @param {*} fallbackValue - Value to return if error occurs
 * @param {string} errorMessage - Custom error message
 * @returns {Promise<*>} Function result or fallback value
 */
export async function safeExecuteAsync(fn, fallbackValue = null, errorMessage = null) {
    try {
        return await fn();
    } catch (error) {
        handleError(error, errorMessage);
        return fallbackValue;
    }
}

/**
 * Retry a function with exponential backoff.
 *
 * @param {Function} fn - Async function to retry
 * @param {Object} options - Retry options
 * @param {number} options.maxRetries - Maximum number of retries (default: 3)
 * @param {number} options.delayMs - Initial delay in ms (default: 1000)
 * @param {number} options.backoffMultiplier - Backoff multiplier (default: 2)
 * @returns {Promise<*>} Function result
 */
export async function retryWithBackoff(fn, options = {}) {
    const {
        maxRetries = 3,
        delayMs = 1000,
        backoffMultiplier = 2
    } = options;

    let lastError;
    let currentDelay = delayMs;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
        try {
            return await fn();
        } catch (error) {
            lastError = error;

            if (attempt < maxRetries) {
                console.log(`Retry attempt ${attempt + 1}/${maxRetries} after ${currentDelay}ms`);
                await new Promise(resolve => setTimeout(resolve, currentDelay));
                currentDelay *= backoffMultiplier;
            }
        }
    }

    // All retries failed
    throw lastError;
}

/**
 * Check if error is a network error.
 *
 * @param {Error} error - Error to check
 * @returns {boolean} True if network error
 */
export function isNetworkError(error) {
    const networkErrors = [
        'Failed to fetch',
        'NetworkError',
        'Network request failed',
        'ECONNREFUSED',
        'ETIMEDOUT'
    ];

    const errorMessage = error instanceof Error ? error.message : String(error);
    return networkErrors.some(msg => errorMessage.includes(msg));
}

/**
 * Check if error is recoverable (can be retried).
 *
 * @param {Error} error - Error to check
 * @returns {boolean} True if recoverable
 */
export function isRecoverableError(error) {
    // Network errors are typically recoverable
    if (isNetworkError(error)) {
        return true;
    }

    // 5xx server errors are typically recoverable
    if (error.status && error.status >= 500 && error.status < 600) {
        return true;
    }

    // Timeout errors are recoverable
    if (error.message && error.message.toLowerCase().includes('timeout')) {
        return true;
    }

    return false;
}
