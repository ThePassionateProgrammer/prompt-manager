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

    def test_silence_detected_transitions_to_sending(self):
        """
        After 10 seconds of silence during transcription, auto-send the message.
        This triggers the AI interaction.
        """
        # Arrange
        state_machine = HandsFreeStateMachine()
        state_machine.start_word_detected()
        assert state_machine.current_state == State.TRANSCRIBING

        # Act
        state_machine.silence_detected()

        # Assert
        assert state_machine.current_state == State.SENDING

    def test_message_sent_transitions_to_waiting_for_reply(self):
        """
        Once message is sent to AI, wait for the response.
        This is a brief transitional state.
        """
        # Arrange
        state_machine = HandsFreeStateMachine()
        state_machine.start_word_detected()
        state_machine.silence_detected()
        assert state_machine.current_state == State.SENDING

        # Act
        state_machine.message_sent()

        # Assert
        assert state_machine.current_state == State.WAITING_FOR_REPLY

    def test_reply_received_transitions_to_playing(self):
        """
        When AI response arrives, play it via text-to-speech.
        User hears the AI response.
        """
        # Arrange
        state_machine = HandsFreeStateMachine()
        state_machine.start_word_detected()
        state_machine.silence_detected()
        state_machine.message_sent()
        assert state_machine.current_state == State.WAITING_FOR_REPLY

        # Act
        state_machine.reply_received()

        # Assert
        assert state_machine.current_state == State.PLAYING

    def test_response_finished_transitions_to_transcribing(self):
        """
        After AI response finishes playing, return to transcribing.
        This completes the conversation loop - ready for next question.
        """
        # Arrange
        state_machine = HandsFreeStateMachine()
        state_machine.start_word_detected()
        state_machine.silence_detected()
        state_machine.message_sent()
        state_machine.reply_received()
        assert state_machine.current_state == State.PLAYING

        # Act
        state_machine.response_finished()

        # Assert
        assert state_machine.current_state == State.TRANSCRIBING

    def test_stop_word_detected_transitions_to_paused(self):
        """
        When stop word heard ("Stop Amber"), pause transcription.
        User wants to temporarily stop without exiting conversation mode.
        """
        # Arrange
        state_machine = HandsFreeStateMachine()
        state_machine.start_word_detected()
        assert state_machine.current_state == State.TRANSCRIBING

        # Act
        state_machine.stop_word_detected()

        # Assert
        assert state_machine.current_state == State.PAUSED

    def test_resume_from_paused_transitions_to_wake_listening(self):
        """
        When resuming from PAUSED, return to WAKE_LISTENING.
        User must say start word again to begin transcribing.
        """
        # Arrange
        state_machine = HandsFreeStateMachine()
        state_machine.start_word_detected()
        state_machine.stop_word_detected()
        assert state_machine.current_state == State.PAUSED

        # Act
        state_machine.resume()

        # Assert
        assert state_machine.current_state == State.WAKE_LISTENING
