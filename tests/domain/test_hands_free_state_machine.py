"""
Tests for HandsFreeStateMachine domain model.

The state machine models the hands-free conversation flow:
- WAKE_LISTENING: Waiting for start word
- TRANSCRIBING: Actively capturing speech
- SENDING: Auto-sending message after silence
- WAITING_FOR_REPLY: AI is processing
- PLAYING: AI response is being spoken
- PAUSED: User manually paused

Test strategy: One state transition at a time, test-first.
"""

import pytest
from src.prompt_manager.domain.hands_free_state_machine import (
    HandsFreeStateMachine,
    State
)


class TestHandsFreeStateMachine:
    """Test suite for hands-free conversation state machine."""

    def test_initial_state_is_wake_listening(self):
        """
        When hands-free mode starts, it should wait for the wake word.
        This is the entry point - user hasn't said anything yet.
        """
        # Arrange & Act
        state_machine = HandsFreeStateMachine()

        # Assert
        assert state_machine.current_state == State.WAKE_LISTENING

    def test_start_word_detected_transitions_to_transcribing(self):
        """
        When system hears start word ("Hey Amber"), begin transcribing.
        This is the key entry point into active conversation.
        """
        # Arrange
        state_machine = HandsFreeStateMachine()
        assert state_machine.current_state == State.WAKE_LISTENING

        # Act
        state_machine.start_word_detected()

        # Assert
        assert state_machine.current_state == State.TRANSCRIBING
