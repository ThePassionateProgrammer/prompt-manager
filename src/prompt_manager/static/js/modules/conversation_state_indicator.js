/**
 * Conversation State Indicator Module
 *
 * Provides visual feedback for conversation mode state changes.
 * Shows the current state (LISTENING, PAUSED, SENDING, PLAYING, IDLE)
 * with appropriate icons, colors, and animations.
 *
 * Dependencies:
 * - Conversation Mode module for state information
 */

let conversationMode = null;
let indicatorElement = null;

/**
 * Initialize the state indicator with dependencies.
 *
 * @param {Object} deps - Dependencies
 * @param {Object} deps.conversationMode - Conversation mode state machine
 */
export function initializeStateIndicator(deps) {
    conversationMode = deps.conversationMode;
    createIndicatorElement();
}

/**
 * Create the indicator element and add it to the DOM.
 */
function createIndicatorElement() {
    // Create indicator container
    indicatorElement = document.createElement('div');
    indicatorElement.id = 'conversation-state-indicator';
    indicatorElement.className = 'conversation-state-indicator hidden';
    indicatorElement.setAttribute('role', 'status');
    indicatorElement.setAttribute('aria-live', 'polite');

    // Create state icon
    const icon = document.createElement('div');
    icon.className = 'state-icon';
    indicatorElement.appendChild(icon);

    // Create state label
    const label = document.createElement('div');
    label.className = 'state-label';
    label.textContent = 'IDLE';
    indicatorElement.appendChild(label);

    // Add to page (above the conversation mode button)
    const conversationBtn = document.getElementById('conversation-mode-btn');
    if (conversationBtn && conversationBtn.parentElement) {
        conversationBtn.parentElement.insertBefore(indicatorElement, conversationBtn);
    } else {
        // Fallback: add to body
        document.body.appendChild(indicatorElement);
    }
}

/**
 * Update the indicator to show the current state.
 *
 * @param {string} state - The current conversation state
 */
export function updateState(state) {
    if (!indicatorElement) {
        console.warn('State indicator not initialized');
        return;
    }

    // Get state configuration
    const stateConfig = getStateConfig(state);

    // Update indicator visibility
    if (state === 'IDLE') {
        indicatorElement.classList.add('hidden');
    } else {
        indicatorElement.classList.remove('hidden');
    }

    // Update state class
    indicatorElement.className = `conversation-state-indicator ${stateConfig.className}`;

    // Update icon
    const icon = indicatorElement.querySelector('.state-icon');
    if (icon) {
        icon.textContent = stateConfig.icon;
    }

    // Update label
    const label = indicatorElement.querySelector('.state-label');
    if (label) {
        label.textContent = stateConfig.label;
    }

    // Update aria-label for accessibility
    indicatorElement.setAttribute('aria-label', `Conversation mode: ${stateConfig.label}`);
}

/**
 * Get configuration for a specific state.
 *
 * @param {string} state - The conversation state
 * @returns {Object} State configuration
 */
function getStateConfig(state) {
    const configs = {
        IDLE: {
            icon: '',
            label: 'Inactive',
            className: 'state-idle',
        },
        LISTENING: {
            icon: '🎤',
            label: 'Listening...',
            className: 'state-listening',
        },
        PAUSED: {
            icon: '⏸️',
            label: 'Paused',
            className: 'state-paused',
        },
        SENDING: {
            icon: '📤',
            label: 'Sending...',
            className: 'state-sending',
        },
        PLAYING: {
            icon: '🔊',
            label: 'Playing response...',
            className: 'state-playing',
        },
    };

    return configs[state] || configs.IDLE;
}

/**
 * Show a pulse animation on the indicator (e.g., when voice is detected).
 */
export function showPulse() {
    if (!indicatorElement) {
        return;
    }

    indicatorElement.classList.add('pulse');
    setTimeout(() => {
        indicatorElement.classList.remove('pulse');
    }, 600);
}

/**
 * Destroy the indicator and remove it from DOM.
 */
export function destroyIndicator() {
    if (indicatorElement && indicatorElement.parentNode) {
        indicatorElement.remove();
        indicatorElement = null;
    }
}
