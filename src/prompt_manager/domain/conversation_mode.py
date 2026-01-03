"""
Conversation Mode domain model.

Pure business logic for managing conversation mode state machine.
Orchestrates hands-free dialogue loop with zero dependencies.
"""
from enum import Enum


class ConversationState(Enum):
    """States in the conversation mode state machine.

    State Transitions:
    - IDLE: Not in conversation mode (default)
    - LISTENING: Actively listening for user speech
    - PAUSED: Conversation mode active but listening paused
    - SENDING: Sending message to LLM
    - PLAYING: Playing back LLM response
    """
    IDLE = "idle"
    LISTENING = "listening"
    PAUSED = "paused"
    SENDING = "sending"
    PLAYING = "playing"


class ConversationModeStateMachine:
    """State machine for conversation mode.

    Business Rules:
    - Starts in IDLE state (conversation mode off)
    - Activation starts listening automatically
    - Send message transitions from LISTENING/PAUSED to SENDING
    - Response receipt transitions from SENDING to PLAYING
    - Playback completion auto-restarts listening (loop)
    - Can pause/resume listening with mic button
    - Can interrupt playback to speak again
    - Deactivation returns to IDLE from any state
    """

    def __init__(self):
        """Initialize state machine in IDLE state."""
        self.current_state = ConversationState.IDLE
        self.is_active = False

    def activate(self) -> None:
        """Activate conversation mode and start listening.

        Business Rule: Automatically starts listening when activated.

        Raises:
            ValueError: If already active
        """
        if self.is_active:
            raise ValueError("Conversation mode already active")

        self.is_active = True
        self.current_state = ConversationState.LISTENING

    def deactivate(self) -> None:
        """Deactivate conversation mode and return to IDLE.

        Business Rule: Can deactivate from any state.
        """
        self.is_active = False
        self.current_state = ConversationState.IDLE

    def send_message(self) -> None:
        """Transition to SENDING state.

        Business Rules:
        - Can only send if conversation mode is active
        - Can send from LISTENING or PAUSED states
        - Cannot send if already sending or playing

        Raises:
            ValueError: If invalid state transition
        """
        if not self.is_active:
            raise ValueError("Conversation mode not active")

        if self.current_state == ConversationState.SENDING:
            raise ValueError("Already sending message")

        if self.current_state == ConversationState.PLAYING:
            raise ValueError("Cannot send while playing response")

        if self.current_state in (ConversationState.LISTENING, ConversationState.PAUSED):
            self.current_state = ConversationState.SENDING
        else:
            raise ValueError(f"Cannot send from state: {self.current_state}")

    def receive_response(self) -> None:
        """Transition to PLAYING state.

        Business Rule: Can only receive response if waiting for one (SENDING state).

        Raises:
            ValueError: If not in SENDING state
        """
        if self.current_state != ConversationState.SENDING:
            raise ValueError("Not waiting for response (not in SENDING state)")

        self.current_state = ConversationState.PLAYING

    def finish_playback(self) -> None:
        """Finish playing response and auto-restart listening.

        Business Rule: Auto-loops back to LISTENING after playback completes.

        Raises:
            ValueError: If not in PLAYING state
        """
        if self.current_state != ConversationState.PLAYING:
            raise ValueError("Not currently playing response")

        self.current_state = ConversationState.LISTENING

    def pause_listening(self) -> None:
        """Pause listening (user clicks mic button).

        Business Rules:
        - Can only pause from LISTENING state
        - Cannot pause during SENDING or PLAYING

        Raises:
            ValueError: If invalid state transition
        """
        if self.current_state != ConversationState.LISTENING:
            raise ValueError(f"Cannot pause from state: {self.current_state}")

        self.current_state = ConversationState.PAUSED

    def resume_listening(self) -> None:
        """Resume listening from paused state.

        Raises:
            ValueError: If not in PAUSED state
        """
        if self.current_state != ConversationState.PAUSED:
            raise ValueError("Not in paused state")

        self.current_state = ConversationState.LISTENING

    def interrupt_playback(self) -> None:
        """Interrupt playback and return to listening.

        Business Rule: User can interrupt playback to speak again.

        Raises:
            ValueError: If not in PLAYING state
        """
        if self.current_state != ConversationState.PLAYING:
            raise ValueError("Not currently playing response")

        self.current_state = ConversationState.LISTENING

    def should_be_listening(self) -> bool:
        """Query if microphone should be active.

        Returns:
            True if in LISTENING state, False otherwise
        """
        return self.current_state == ConversationState.LISTENING

    def should_auto_play(self) -> bool:
        """Query if response should auto-play.

        Business Rule: Auto-play only when in conversation mode.

        Returns:
            True if in conversation mode and waiting for response
        """
        return self.is_active and self.current_state == ConversationState.SENDING

    def should_auto_restart(self) -> bool:
        """Query if should auto-restart listening after playback.

        Business Rule: Auto-restart only when in conversation mode.

        Returns:
            True if in conversation mode and currently playing
        """
        return self.is_active and self.current_state == ConversationState.PLAYING
