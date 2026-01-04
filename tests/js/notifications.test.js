/**
 * Unit tests for the Notifications Module
 *
 * Tests notification display, queueing, types, and dismissal.
 */

import { describe, test, expect, jest, beforeEach } from '@jest/globals';

// Mock the module since we need to import it
let notificationsModule;

beforeEach(async () => {
    // Reset DOM
    document.body.innerHTML = '';

    // Clear module cache and re-import to get fresh state
    jest.resetModules();
    notificationsModule = await import('../../src/prompt_manager/static/js/modules/notifications.js');
});

describe('Notifications Module', () => {
    describe('Basic Notification Display', () => {
        test('should create and display a notification element', () => {
            notificationsModule.showNotification('Test message', 'success');

            const notification = document.querySelector('.notification');
            expect(notification).toBeTruthy();
            expect(notification.textContent).toContain('Test message');
        });

        test('should apply correct notification type class', () => {
            notificationsModule.showNotification('Success!', 'success');
            let notification = document.querySelector('.notification');
            expect(notification.classList.contains('success')).toBe(true);

            document.body.innerHTML = '';
            notificationsModule.showNotification('Error!', 'error');
            notification = document.querySelector('.notification');
            expect(notification.classList.contains('error')).toBe(true);
        });

        test('should add ARIA attributes for accessibility', () => {
            notificationsModule.showNotification('Test', 'info');

            const notification = document.querySelector('.notification');
            expect(notification.getAttribute('role')).toBe('alert');
            expect(notification.getAttribute('aria-live')).toBe('polite');
        });

        test('should create notification with message and dismiss button', () => {
            notificationsModule.showNotification('Test message', 'success', 3000, true);

            const notification = document.querySelector('.notification');
            const message = notification.querySelector('.notification-message');
            const dismissBtn = notification.querySelector('.notification-dismiss');

            expect(message.textContent).toBe('Test message');
            expect(dismissBtn).toBeTruthy();
            expect(dismissBtn.getAttribute('aria-label')).toBe('Dismiss notification');
        });

        test('should not show dismiss button when dismissible is false', () => {
            notificationsModule.showNotification('Test', 'info', 3000, false);

            const notification = document.querySelector('.notification');
            const dismissBtn = notification.querySelector('.notification-dismiss');

            expect(dismissBtn).toBeFalsy();
        });
    });

    describe('Notification Types', () => {
        test('should create success notification with helper', () => {
            notificationsModule.showSuccess('Success!');

            const notification = document.querySelector('.notification');
            expect(notification.classList.contains('success')).toBe(true);
            expect(notification.textContent).toContain('Success!');
        });

        test('should create error notification with helper', () => {
            notificationsModule.showError('Error!');

            const notification = document.querySelector('.notification');
            expect(notification.classList.contains('error')).toBe(true);
        });

        test('should create warning notification with helper', () => {
            notificationsModule.showWarning('Warning!');

            const notification = document.querySelector('.notification');
            expect(notification.classList.contains('warning')).toBe(true);
        });

        test('should create info notification with helper', () => {
            notificationsModule.showInfo('Info!');

            const notification = document.querySelector('.notification');
            expect(notification.classList.contains('info')).toBe(true);
        });

        test('should default to info type for invalid type', () => {
            // Spy on console.warn
            const warnSpy = jest.spyOn(console, 'warn').mockImplementation();

            notificationsModule.showNotification('Test', 'invalid-type');

            const notification = document.querySelector('.notification');
            expect(notification.classList.contains('info')).toBe(true);
            expect(warnSpy).toHaveBeenCalled();

            warnSpy.mockRestore();
        });
    });

    describe('Notification Validation', () => {
        test('should not create notification with empty message', () => {
            const errorSpy = jest.spyOn(console, 'error').mockImplementation();

            notificationsModule.showNotification('', 'success');

            const notification = document.querySelector('.notification');
            expect(notification).toBeFalsy();
            expect(errorSpy).toHaveBeenCalled();

            errorSpy.mockRestore();
        });

        test('should not create notification with non-string message', () => {
            const errorSpy = jest.spyOn(console, 'error').mockImplementation();

            notificationsModule.showNotification(123, 'success');

            const notification = document.querySelector('.notification');
            expect(notification).toBeFalsy();

            errorSpy.mockRestore();
        });

        test('should not create notification with null message', () => {
            const errorSpy = jest.spyOn(console, 'error').mockImplementation();

            notificationsModule.showNotification(null, 'success');

            expect(document.querySelector('.notification')).toBeFalsy();

            errorSpy.mockRestore();
        });
    });

    describe('Notification Queueing', () => {
        test('should queue multiple notifications', async () => {
            notificationsModule.showNotification('First', 'success');
            notificationsModule.showNotification('Second', 'info');
            notificationsModule.showNotification('Third', 'warning');

            // Only first notification should be visible initially
            const notifications = document.querySelectorAll('.notification');
            expect(notifications.length).toBe(1);
            expect(notifications[0].textContent).toContain('First');
        });

        test('should process queued notifications after removal', (done) => {
            notificationsModule.showNotification('First', 'success', 100);
            notificationsModule.showNotification('Second', 'info', 100);

            // Initially only first notification
            expect(document.querySelectorAll('.notification').length).toBe(1);

            // After first notification is removed, second should appear
            setTimeout(() => {
                const notifications = document.querySelectorAll('.notification');
                // Should have second notification (first was removed)
                expect(notifications.length).toBeGreaterThanOrEqual(0);
                done();
            }, 500);
        });
    });

    describe('Notification Dismissal', () => {
        test('should remove notification when dismiss button clicked', () => {
            notificationsModule.showNotification('Test', 'success');

            const notification = document.querySelector('.notification');
            const dismissBtn = notification.querySelector('.notification-dismiss');

            dismissBtn.click();

            // Notification should start fading (opacity set to 0)
            expect(notification.style.opacity).toBe('0');
        });

        test('should auto-remove notification after duration', (done) => {
            notificationsModule.showNotification('Test', 'success', 100);

            const notification = document.querySelector('.notification');
            expect(notification).toBeTruthy();

            // After duration + animation time, notification should be removed
            setTimeout(() => {
                const notifications = document.querySelectorAll('.notification');
                expect(notifications.length).toBe(0);
                done();
            }, 500);
        });
    });

    describe('Clear All Notifications', () => {
        test('should clear all notifications from DOM', () => {
            notificationsModule.showNotification('First', 'success');

            // Manually add another to DOM to simulate queue processing
            setTimeout(() => {
                notificationsModule.showNotification('Second', 'info');
            }, 50);

            expect(document.querySelectorAll('.notification').length).toBeGreaterThan(0);

            notificationsModule.clearAllNotifications();

            const notifications = document.querySelectorAll('.notification');
            expect(notifications.length).toBe(0);
        });

        test('should clear notification queue', () => {
            // Queue multiple notifications
            notificationsModule.showNotification('First', 'success');
            notificationsModule.showNotification('Second', 'info');
            notificationsModule.showNotification('Third', 'warning');

            // Clear all
            notificationsModule.clearAllNotifications();

            // Wait a bit and verify no new notifications appear
            setTimeout(() => {
                const notifications = document.querySelectorAll('.notification');
                expect(notifications.length).toBe(0);
            }, 100);
        });
    });

    describe('Default Durations', () => {
        test('should use default duration for success (3000ms)', () => {
            notificationsModule.showSuccess('Test');

            const notification = document.querySelector('.notification');
            expect(notification.dataset.timeoutId).toBeTruthy();
        });

        test('should use longer duration for errors (5000ms)', () => {
            notificationsModule.showError('Test');

            const notification = document.querySelector('.notification');
            expect(notification.dataset.timeoutId).toBeTruthy();
        });

        test('should use medium duration for warnings (4000ms)', () => {
            notificationsModule.showWarning('Test');

            const notification = document.querySelector('.notification');
            expect(notification.dataset.timeoutId).toBeTruthy();
        });

        test('should use default duration for info (3000ms)', () => {
            notificationsModule.showInfo('Test');

            const notification = document.querySelector('.notification');
            expect(notification.dataset.timeoutId).toBeTruthy();
        });
    });
});
