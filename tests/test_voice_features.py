"""
Tests for voice interaction features.

Voice features use Browser Web Speech API:
- Speech-to-text: webkitSpeechRecognition
- Text-to-speech: speechSynthesis

These are JavaScript features, so we test the integration points and state management.
"""
import pytest
from src.prompt_manager.domain.voice_interaction import VoiceInteractionManager


class TestVoiceInteractionManager:
    """Test the domain model for voice interaction state."""

    def test_create_voice_manager(self):
        """Can create a voice interaction manager."""
        manager = VoiceInteractionManager()
        assert manager is not None
        assert manager.is_listening is False
        assert manager.is_speaking is False

    def test_start_listening(self):
        """Can start listening for speech input."""
        manager = VoiceInteractionManager()
        manager.start_listening()
        assert manager.is_listening is True

    def test_stop_listening(self):
        """Can stop listening for speech input."""
        manager = VoiceInteractionManager()
        manager.start_listening()
        manager.stop_listening()
        assert manager.is_listening is False

    def test_cannot_start_listening_while_already_listening(self):
        """Business Rule: Cannot start listening if already listening."""
        manager = VoiceInteractionManager()
        manager.start_listening()

        with pytest.raises(ValueError, match="Already listening"):
            manager.start_listening()

    def test_start_speaking(self):
        """Can start speaking text."""
        manager = VoiceInteractionManager()
        manager.start_speaking("Hello world")
        assert manager.is_speaking is True
        assert manager.current_text == "Hello world"

    def test_stop_speaking(self):
        """Can stop speaking."""
        manager = VoiceInteractionManager()
        manager.start_speaking("Hello world")
        manager.stop_speaking()
        assert manager.is_speaking is False
        assert manager.current_text is None

    def test_cannot_start_speaking_while_already_speaking(self):
        """Business Rule: Cannot start speaking if already speaking."""
        manager = VoiceInteractionManager()
        manager.start_speaking("First text")

        with pytest.raises(ValueError, match="Already speaking"):
            manager.start_speaking("Second text")

    def test_cannot_speak_empty_text(self):
        """Business Rule: Cannot speak empty or whitespace text."""
        manager = VoiceInteractionManager()

        with pytest.raises(ValueError, match="Text cannot be empty"):
            manager.start_speaking("")

        with pytest.raises(ValueError, match="Text cannot be empty"):
            manager.start_speaking("   ")

    def test_record_transcript(self):
        """Can record a speech transcript."""
        manager = VoiceInteractionManager()
        manager.record_transcript("Hello from speech")

        assert len(manager.transcripts) == 1
        assert manager.transcripts[0] == "Hello from speech"

    def test_get_latest_transcript(self):
        """Can get the most recent transcript."""
        manager = VoiceInteractionManager()
        manager.record_transcript("First")
        manager.record_transcript("Second")
        manager.record_transcript("Third")

        assert manager.get_latest_transcript() == "Third"

    def test_get_latest_transcript_when_empty(self):
        """Returns None when no transcripts exist."""
        manager = VoiceInteractionManager()
        assert manager.get_latest_transcript() is None

    def test_clear_transcripts(self):
        """Can clear all transcripts."""
        manager = VoiceInteractionManager()
        manager.record_transcript("First")
        manager.record_transcript("Second")

        manager.clear_transcripts()
        assert len(manager.transcripts) == 0
        assert manager.get_latest_transcript() is None

    def test_reset_state(self):
        """Can reset all voice interaction state."""
        manager = VoiceInteractionManager()
        manager.start_listening()
        manager.record_transcript("Test")
        manager.start_speaking("Response")

        manager.reset()

        assert manager.is_listening is False
        assert manager.is_speaking is False
        assert len(manager.transcripts) == 0
        assert manager.current_text is None


class TestSpeechRecognitionConfig:
    """Test configuration for speech recognition."""

    def test_default_language(self):
        """Default language is en-US."""
        manager = VoiceInteractionManager()
        assert manager.language == "en-US"

    def test_custom_language(self):
        """Can set custom language."""
        manager = VoiceInteractionManager(language="es-ES")
        assert manager.language == "es-ES"

    def test_default_continuous_mode(self):
        """Continuous mode is False by default (single utterance)."""
        manager = VoiceInteractionManager()
        assert manager.continuous is False

    def test_enable_continuous_mode(self):
        """Can enable continuous mode."""
        manager = VoiceInteractionManager(continuous=True)
        assert manager.continuous is True


class TestSpeechSynthesisConfig:
    """Test configuration for speech synthesis."""

    def test_default_voice_settings(self):
        """Default voice settings are reasonable."""
        manager = VoiceInteractionManager()
        assert manager.voice_rate == 1.0  # Normal speed
        assert manager.voice_pitch == 1.0  # Normal pitch
        assert manager.voice_volume == 1.0  # Full volume

    def test_custom_voice_settings(self):
        """Can customize voice settings."""
        manager = VoiceInteractionManager(
            voice_rate=1.5,
            voice_pitch=0.8,
            voice_volume=0.9
        )
        assert manager.voice_rate == 1.5
        assert manager.voice_pitch == 0.8
        assert manager.voice_volume == 0.9

    def test_voice_rate_bounds(self):
        """Voice rate must be between 0.1 and 10."""
        with pytest.raises(ValueError, match="Voice rate must be between"):
            VoiceInteractionManager(voice_rate=0.05)

        with pytest.raises(ValueError, match="Voice rate must be between"):
            VoiceInteractionManager(voice_rate=15)

    def test_voice_pitch_bounds(self):
        """Voice pitch must be between 0 and 2."""
        with pytest.raises(ValueError, match="Voice pitch must be between"):
            VoiceInteractionManager(voice_pitch=-0.1)

        with pytest.raises(ValueError, match="Voice pitch must be between"):
            VoiceInteractionManager(voice_pitch=2.5)

    def test_voice_volume_bounds(self):
        """Voice volume must be between 0 and 1."""
        with pytest.raises(ValueError, match="Voice volume must be between"):
            VoiceInteractionManager(voice_volume=-0.1)

        with pytest.raises(ValueError, match="Voice volume must be between"):
            VoiceInteractionManager(voice_volume=1.5)
