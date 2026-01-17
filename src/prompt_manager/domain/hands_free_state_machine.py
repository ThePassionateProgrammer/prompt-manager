"""
HandsFreeStateMachine - Domain model for hands-free conversation flow.

Pure domain logic with no external dependencies.
Models the state transitions for hands-free voice interaction.
"""

from enum import Enum, auto


class State(Enum):
    """States in the hands-free conversation flow."""
    WAKE_LISTENING = auto()    # Waiting for start word ("Hey Amber")
    TRANSCRIBING = auto()      # Actively capturing speech
    SENDING = auto()           # Auto-sending message after silence
    WAITING_FOR_REPLY = auto() # AI is processing the message
    PLAYING = auto()           # AI response is being spoken
    PAUSED = auto()            # User manually paused transcription


class HandsFreeStateMachine:
    """
    State machine for hands-free conversation mode.

    Manages transitions between different states of the conversation flow.
    Pure domain model - no I/O, no side effects.
    """

    def __init__(self):
        """Initialize state machine in WAKE_LISTENING state."""
        self.current_state = State.WAKE_LISTENING

    def start_word_detected(self):
        """
        Transition to TRANSCRIBING when start word is heard.
        Only valid from WAKE_LISTENING state.
        """
        if self.current_state == State.WAKE_LISTENING:
            self.current_state = State.TRANSCRIBING

    def silence_detected(self):
        """
        Transition to SENDING after silence threshold reached.
        Only valid from TRANSCRIBING state (user has stopped talking).
        """
        if self.current_state == State.TRANSCRIBING:
            self.current_state = State.SENDING
