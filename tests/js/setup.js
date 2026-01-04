/**
 * Jest setup file for JavaScript tests
 *
 * Sets up global mocks and utilities for testing browser-based JavaScript modules.
 */

import { jest } from '@jest/globals';

// Mock localStorage
const localStorageMock = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock speechSynthesis
global.speechSynthesis = {
    speak: jest.fn(),
    cancel: jest.fn(),
    pause: jest.fn(),
    resume: jest.fn(),
    getVoices: jest.fn(() => []),
    onvoiceschanged: null,
};

// Mock SpeechSynthesisUtterance
global.SpeechSynthesisUtterance = jest.fn().mockImplementation((text) => ({
    text,
    lang: 'en-US',
    voice: null,
    volume: 1,
    rate: 1,
    pitch: 1,
    onstart: null,
    onend: null,
    onerror: null,
}));

// Mock SpeechRecognition
global.SpeechRecognition = jest.fn().mockImplementation(() => ({
    continuous: false,
    interimResults: false,
    lang: 'en-US',
    start: jest.fn(),
    stop: jest.fn(),
    abort: jest.fn(),
    onresult: null,
    onerror: null,
    onend: null,
    onstart: null,
}));

// Also mock webkit version
global.webkitSpeechRecognition = global.SpeechRecognition;

// Reset all mocks before each test
beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
    document.body.innerHTML = '';
});
