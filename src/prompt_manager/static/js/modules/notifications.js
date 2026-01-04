/**
 * Notification Module
 *
 * Centralized notification system with error handling and queueing.
 * Provides a consistent way to show success, error, warning, and info messages.
 *
 * Features:
 * - Automatic timeout and cleanup
 * - Multiple notification types (success, error, warning, info)
 * - Notification queue to prevent overlap
 * - Slide-in animations
 * - Manual dismissal option
 */

// Notification queue to manage multiple notifications
const notificationQueue = [];
let isShowingNotification = false;

/**
 * Show a notification message to the user.
 *
 * @param {string} message - The message to display
 * @param {string} type - Type of notification: 'success', 'error', 'warning', 'info'
 * @param {number} duration - How long to show the notification in ms (default: 3000)
 * @param {boolean} dismissible - Whether the notification can be manually dismissed (default: true)
 */
export function showNotification(message, type = 'success', duration = 3000, dismissible = true) {
    // Validate parameters
    if (!message || typeof message !== 'string') {
        console.error('showNotification: message must be a non-empty string');
        return;
    }

    const validTypes = ['success', 'error', 'warning', 'info'];
    if (!validTypes.includes(type)) {
        console.warn(`showNotification: invalid type "${type}", defaulting to "info"`);
        type = 'info';
    }

    // Queue the notification
    notificationQueue.push({ message, type, duration, dismissible });
    processNotificationQueue();
}

/**
 * Process the notification queue.
 * Shows notifications one at a time with proper timing.
 */
function processNotificationQueue() {
    if (isShowingNotification || notificationQueue.length === 0) {
        return;
    }

    isShowingNotification = true;
    const { message, type, duration, dismissible } = notificationQueue.shift();

    try {
        displayNotification(message, type, duration, dismissible);
    } catch (error) {
        console.error('Error displaying notification:', error);
        isShowingNotification = false;
        // Continue processing queue even if one notification fails
        processNotificationQueue();
    }
}

/**
 * Display a notification on screen.
 *
 * @param {string} message - The message to display
 * @param {string} type - Type of notification
 * @param {number} duration - How long to show the notification
 * @param {boolean} dismissible - Whether the notification can be dismissed
 */
function displayNotification(message, type, duration, dismissible) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.setAttribute('role', 'alert');
    notification.setAttribute('aria-live', 'polite');

    // Create message text
    const messageSpan = document.createElement('span');
    messageSpan.className = 'notification-message';
    messageSpan.textContent = message;
    notification.appendChild(messageSpan);

    // Add dismiss button if dismissible
    if (dismissible) {
        const dismissBtn = document.createElement('button');
        dismissBtn.className = 'notification-dismiss';
        dismissBtn.innerHTML = '&times;';
        dismissBtn.setAttribute('aria-label', 'Dismiss notification');
        dismissBtn.onclick = () => removeNotification(notification);
        notification.appendChild(dismissBtn);
    }

    // Add to DOM
    document.body.appendChild(notification);

    // Auto-remove after duration
    const timeoutId = setTimeout(() => {
        removeNotification(notification);
    }, duration);

    // Store timeout ID for potential early removal
    notification.dataset.timeoutId = timeoutId;
}

/**
 * Remove a notification from the DOM.
 *
 * @param {HTMLElement} notification - The notification element to remove
 */
function removeNotification(notification) {
    if (!notification || !notification.parentNode) {
        return;
    }

    // Clear the timeout if it exists
    if (notification.dataset.timeoutId) {
        clearTimeout(parseInt(notification.dataset.timeoutId));
    }

    // Add fade-out animation
    notification.style.opacity = '0';
    notification.style.transform = 'translateX(400px)';

    // Remove from DOM after animation
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
        isShowingNotification = false;
        // Process next notification in queue
        processNotificationQueue();
    }, 300);
}

/**
 * Show a success notification.
 *
 * @param {string} message - Success message
 * @param {number} duration - Duration in ms (optional)
 */
export function showSuccess(message, duration = 3000) {
    showNotification(message, 'success', duration);
}

/**
 * Show an error notification.
 *
 * @param {string} message - Error message
 * @param {number} duration - Duration in ms (optional, defaults to 5000 for errors)
 */
export function showError(message, duration = 5000) {
    showNotification(message, 'error', duration);
}

/**
 * Show a warning notification.
 *
 * @param {string} message - Warning message
 * @param {number} duration - Duration in ms (optional)
 */
export function showWarning(message, duration = 4000) {
    showNotification(message, 'warning', duration);
}

/**
 * Show an info notification.
 *
 * @param {string} message - Info message
 * @param {number} duration - Duration in ms (optional)
 */
export function showInfo(message, duration = 3000) {
    showNotification(message, 'info', duration);
}

/**
 * Clear all notifications from the screen and queue.
 */
export function clearAllNotifications() {
    // Clear queue
    notificationQueue.length = 0;

    // Remove all notifications from DOM
    const notifications = document.querySelectorAll('.notification');
    notifications.forEach(notification => {
        if (notification.dataset.timeoutId) {
            clearTimeout(parseInt(notification.dataset.timeoutId));
        }
        notification.remove();
    });

    isShowingNotification = false;
}
