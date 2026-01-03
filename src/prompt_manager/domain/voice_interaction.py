"""
Voice Interaction domain model.

Pure business logic for managing voice interaction state with zero dependencies.
Coordinates with Browser Web Speech API (webkitSpeechRecognition and speechSynthesis).
"""
from typing import List, Optional


class VoiceInteractionManager:
    """Manages state for voice interaction features.

    Business Rules:
    - Cannot start listening if already listening
    - Cannot start speaking if already speaking
    - Text to speak must be non-empty
    - Voice settings must be within valid bounds
    - Transcripts are recorded and can be retrieved
    """

    def __init__(
        self,
        language: str = "en-US",
        continuous: bool = False,
        voice_rate: float = 1.0,
        voice_pitch: float = 1.0,
        voice_volume: float = 1.0
    ):
        """Initialize voice interaction manager.

        Args:
            language: Language code for speech recognition (default: en-US)
            continuous: Whether to use continuous recognition mode (default: False)
            voice_rate: Speech rate for synthesis, 0.1-10 (default: 1.0)
            voice_pitch: Speech pitch for synthesis, 0-2 (default: 1.0)
            voice_volume: Speech volume for synthesis, 0-1 (default: 1.0)

        Raises:
            ValueError: If voice settings are out of bounds
        """
        # Speech recognition settings
        self.language = language
        self.continuous = continuous

        # Validate and set voice synthesis settings
        if not 0.1 <= voice_rate <= 10:
            raise ValueError("Voice rate must be between 0.1 and 10")
        if not 0 <= voice_pitch <= 2:
            raise ValueError("Voice pitch must be between 0 and 2")
        if not 0 <= voice_volume <= 1:
            raise ValueError("Voice volume must be between 0 and 1")

        self.voice_rate = voice_rate
        self.voice_pitch = voice_pitch
        self.voice_volume = voice_volume

        # State tracking
        self.is_listening: bool = False
        self.is_speaking: bool = False
        self.current_text: Optional[str] = None
        self.transcripts: List[str] = []

    def start_listening(self) -> None:
        """Start listening for speech input.

        Business Rule: Cannot start if already listening.

        Raises:
            ValueError: If already listening
        """
        if self.is_listening:
            raise ValueError("Already listening")

        self.is_listening = True

    def stop_listening(self) -> None:
        """Stop listening for speech input."""
        self.is_listening = False

    def start_speaking(self, text: str) -> None:
        """Start speaking text.

        Business Rules:
        - Text must be non-empty
        - Cannot start if already speaking

        Args:
            text: Text to speak

        Raises:
            ValueError: If text is empty or already speaking
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        if self.is_speaking:
            raise ValueError("Already speaking")

        self.is_speaking = True
        self.current_text = text

    def stop_speaking(self) -> None:
        """Stop speaking."""
        self.is_speaking = False
        self.current_text = None

    def record_transcript(self, text: str) -> None:
        """Record a speech transcript.

        Args:
            text: Transcribed text from speech recognition
        """
        self.transcripts.append(text)

    def get_latest_transcript(self) -> Optional[str]:
        """Get the most recent transcript.

        Returns:
            Latest transcript or None if no transcripts exist
        """
        if not self.transcripts:
            return None
        return self.transcripts[-1]

    def clear_transcripts(self) -> None:
        """Clear all recorded transcripts."""
        self.transcripts = []

    def reset(self) -> None:
        """Reset all voice interaction state.

        Business Rule: Stops any active listening/speaking and clears history.
        """
        self.is_listening = False
        self.is_speaking = False
        self.current_text = None
        self.transcripts = []
