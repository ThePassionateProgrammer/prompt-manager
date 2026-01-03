"""
Tests for Conversation Mode state machine.

Conversation Mode orchestrates a hands-free dialogue loop:
1. User toggles ON → Auto-start listening
2. User speaks → Transcript captured
3. User clicks Send → Stop listening, send message
4. LLM responds → Auto-play response
5. Response finishes → Auto-restart listening
6. Loop continues until toggle OFF
"""
import pytest
from src.prompt_manager.domain.conversation_mode import ConversationModeStateMachine, ConversationState


class TestConversationModeCreation:
    """Test creating and initializing conversation mode."""

    def test_create_state_machine(self):
        """Can create a conversation mode state machine."""
        sm = ConversationModeStateMachine()
        assert sm is not None
        assert sm.current_state == ConversationState.IDLE
        assert sm.is_active is False

    def test_initial_state_is_idle(self):
        """Initial state is IDLE (conversation mode off)."""
        sm = ConversationModeStateMachine()
        assert sm.current_state == ConversationState.IDLE


class TestActivatingConversationMode:
    """Test turning conversation mode ON."""

    def test_activate_conversation_mode(self):
        """Activating conversation mode transitions to LISTENING."""
        sm = ConversationModeStateMachine()
        sm.activate()

        assert sm.is_active is True
        assert sm.current_state == ConversationState.LISTENING

    def test_cannot_activate_if_already_active(self):
        """Business Rule: Cannot activate if already active."""
        sm = ConversationModeStateMachine()
        sm.activate()

        with pytest.raises(ValueError, match="already active"):
            sm.activate()


class TestDeactivatingConversationMode:
    """Test turning conversation mode OFF."""

    def test_deactivate_conversation_mode(self):
        """Deactivating returns to IDLE state."""
        sm = ConversationModeStateMachine()
        sm.activate()
        sm.deactivate()

        assert sm.is_active is False
        assert sm.current_state == ConversationState.IDLE

    def test_can_deactivate_from_any_state(self):
        """Can deactivate from LISTENING, SENDING, or PLAYING."""
        # From LISTENING
        sm = ConversationModeStateMachine()
        sm.activate()  # → LISTENING
        sm.deactivate()
        assert sm.current_state == ConversationState.IDLE

        # From SENDING
        sm = ConversationModeStateMachine()
        sm.activate()  # → LISTENING
        sm.send_message()  # → SENDING
        sm.deactivate()
        assert sm.current_state == ConversationState.IDLE

        # From PLAYING
        sm = ConversationModeStateMachine()
        sm.activate()  # → LISTENING
        sm.send_message()  # → SENDING
        sm.receive_response()  # → PLAYING
        sm.deactivate()
        assert sm.current_state == ConversationState.IDLE


class TestStateTransitions:
    """Test state machine transitions through the conversation loop."""

    def test_listening_to_sending(self):
        """User clicks Send → LISTENING to SENDING."""
        sm = ConversationModeStateMachine()
        sm.activate()  # → LISTENING

        sm.send_message()
        assert sm.current_state == ConversationState.SENDING

    def test_sending_to_playing(self):
        """LLM responds → SENDING to PLAYING."""
        sm = ConversationModeStateMachine()
        sm.activate()  # → LISTENING
        sm.send_message()  # → SENDING

        sm.receive_response()
        assert sm.current_state == ConversationState.PLAYING

    def test_playing_to_listening(self):
        """Response finishes → PLAYING to LISTENING (auto-loop)."""
        sm = ConversationModeStateMachine()
        sm.activate()  # → LISTENING
        sm.send_message()  # → SENDING
        sm.receive_response()  # → PLAYING

        sm.finish_playback()
        assert sm.current_state == ConversationState.LISTENING

    def test_complete_conversation_loop(self):
        """Complete loop: LISTENING → SENDING → PLAYING → LISTENING."""
        sm = ConversationModeStateMachine()

        # Start conversation mode
        sm.activate()
        assert sm.current_state == ConversationState.LISTENING

        # User sends message
        sm.send_message()
        assert sm.current_state == ConversationState.SENDING

        # LLM responds
        sm.receive_response()
        assert sm.current_state == ConversationState.PLAYING

        # Playback finishes, auto-loop back to listening
        sm.finish_playback()
        assert sm.current_state == ConversationState.LISTENING
        assert sm.is_active is True  # Still in conversation mode


class TestInvalidTransitions:
    """Test that invalid state transitions are prevented."""

    def test_cannot_send_message_when_idle(self):
        """Cannot send message if not in conversation mode."""
        sm = ConversationModeStateMachine()

        with pytest.raises(ValueError, match="not active"):
            sm.send_message()

    def test_cannot_send_message_when_sending(self):
        """Cannot send message while already sending."""
        sm = ConversationModeStateMachine()
        sm.activate()  # → LISTENING
        sm.send_message()  # → SENDING

        with pytest.raises(ValueError, match="Already sending"):
            sm.send_message()

    def test_cannot_send_message_when_playing(self):
        """Cannot send message while playing response."""
        sm = ConversationModeStateMachine()
        sm.activate()  # → LISTENING
        sm.send_message()  # → SENDING
        sm.receive_response()  # → PLAYING

        with pytest.raises(ValueError, match="Cannot send"):
            sm.send_message()

    def test_cannot_receive_response_when_listening(self):
        """Cannot receive response if not sending."""
        sm = ConversationModeStateMachine()
        sm.activate()  # → LISTENING

        with pytest.raises(ValueError, match="Not waiting for response"):
            sm.receive_response()

    def test_cannot_finish_playback_when_not_playing(self):
        """Cannot finish playback if not playing."""
        sm = ConversationModeStateMachine()
        sm.activate()  # → LISTENING

        with pytest.raises(ValueError, match="Not currently playing"):
            sm.finish_playback()


class TestPausingAndResuming:
    """Test pausing conversation mode (mic button during conversation mode)."""

    def test_pause_listening(self):
        """Can pause listening (user clicks mic button)."""
        sm = ConversationModeStateMachine()
        sm.activate()  # → LISTENING

        sm.pause_listening()
        assert sm.current_state == ConversationState.PAUSED
        assert sm.is_active is True  # Still in conversation mode

    def test_resume_listening(self):
        """Can resume listening from paused state."""
        sm = ConversationModeStateMachine()
        sm.activate()  # → LISTENING
        sm.pause_listening()  # → PAUSED

        sm.resume_listening()
        assert sm.current_state == ConversationState.LISTENING

    def test_cannot_pause_when_sending(self):
        """Cannot pause while sending message."""
        sm = ConversationModeStateMachine()
        sm.activate()  # → LISTENING
        sm.send_message()  # → SENDING

        with pytest.raises(ValueError, match="Cannot pause"):
            sm.pause_listening()

    def test_cannot_pause_when_playing(self):
        """Cannot pause while playing response."""
        sm = ConversationModeStateMachine()
        sm.activate()  # → LISTENING
        sm.send_message()  # → SENDING
        sm.receive_response()  # → PLAYING

        with pytest.raises(ValueError, match="Cannot pause"):
            sm.pause_listening()

    def test_can_send_from_paused_state(self):
        """Can send message from paused state."""
        sm = ConversationModeStateMachine()
        sm.activate()  # → LISTENING
        sm.pause_listening()  # → PAUSED

        sm.send_message()
        assert sm.current_state == ConversationState.SENDING


class TestInterruptingPlayback:
    """Test interrupting response playback (user speaks during playback)."""

    def test_interrupt_playback_to_send(self):
        """User can interrupt playback by sending new message."""
        sm = ConversationModeStateMachine()
        sm.activate()  # → LISTENING
        sm.send_message()  # → SENDING
        sm.receive_response()  # → PLAYING

        sm.interrupt_playback()
        assert sm.current_state == ConversationState.LISTENING

    def test_interrupted_playback_allows_immediate_send(self):
        """After interrupting playback, can immediately send."""
        sm = ConversationModeStateMachine()
        sm.activate()  # → LISTENING
        sm.send_message()  # → SENDING
        sm.receive_response()  # → PLAYING
        sm.interrupt_playback()  # → LISTENING

        sm.send_message()
        assert sm.current_state == ConversationState.SENDING


class TestStateQueries:
    """Test querying current state information."""

    def test_should_be_listening(self):
        """Query if state machine should be listening."""
        sm = ConversationModeStateMachine()

        assert sm.should_be_listening() is False

        sm.activate()
        assert sm.should_be_listening() is True

        sm.send_message()
        assert sm.should_be_listening() is False

    def test_should_auto_play_response(self):
        """Query if response should auto-play."""
        sm = ConversationModeStateMachine()

        # Not in conversation mode
        assert sm.should_auto_play() is False

        # In conversation mode
        sm.activate()
        sm.send_message()
        assert sm.should_auto_play() is True

    def test_should_auto_restart_after_playback(self):
        """Query if should auto-restart listening after playback."""
        sm = ConversationModeStateMachine()

        # Not in conversation mode
        assert sm.should_auto_restart() is False

        # In conversation mode, after playback
        sm.activate()
        sm.send_message()
        sm.receive_response()
        assert sm.should_auto_restart() is True
