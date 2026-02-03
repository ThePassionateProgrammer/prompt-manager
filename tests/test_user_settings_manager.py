"""
Tests for UserSettingsManager - persistent settings storage.

Test-first development: Comprehensive coverage for settings persistence.
"""
import pytest
import json
import tempfile
from pathlib import Path
from src.prompt_manager.business.user_settings_manager import UserSettingsManager


@pytest.fixture
def temp_settings_file():
    """Create a temporary settings file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({}, f)
        return Path(f.name)


@pytest.fixture
def settings_manager(temp_settings_file):
    """Create a UserSettingsManager with a temporary file."""
    return UserSettingsManager(settings_file=temp_settings_file)


class TestUserSettingsManagerCreation:
    """Test settings manager initialization."""

    def test_creates_settings_file_if_not_exists(self, tmp_path):
        """Should create settings file with defaults if it doesn't exist."""
        settings_file = tmp_path / "test_settings.json"
        assert not settings_file.exists()

        manager = UserSettingsManager(settings_file=settings_file)

        assert settings_file.exists()

    def test_creates_parent_directories(self, tmp_path):
        """Should create parent directories if they don't exist."""
        settings_file = tmp_path / "nested" / "dir" / "settings.json"
        assert not settings_file.parent.exists()

        manager = UserSettingsManager(settings_file=settings_file)

        assert settings_file.exists()

    def test_default_settings_populated(self, tmp_path):
        """Should populate default settings on creation."""
        settings_file = tmp_path / "test_settings.json"
        manager = UserSettingsManager(settings_file=settings_file)

        with open(settings_file, 'r') as f:
            settings = json.load(f)

        assert 'system_prompt' in settings
        assert 'default_provider' in settings
        assert 'default_model' in settings
        assert 'temperature' in settings
        assert 'max_tokens' in settings


class TestSystemPromptPersistence:
    """Test system prompt storage and retrieval."""

    def test_get_system_prompt_returns_default(self, settings_manager):
        """Should return default prompt when none set."""
        prompt = settings_manager.get_system_prompt()
        assert prompt is not None
        assert len(prompt) > 0

    def test_set_and_get_system_prompt(self, settings_manager):
        """Should persist and retrieve custom system prompt."""
        custom_prompt = "You are a coding assistant specialized in Python."
        settings_manager.set_system_prompt(custom_prompt)

        result = settings_manager.get_system_prompt()
        assert result == custom_prompt

    def test_system_prompt_survives_reload(self, temp_settings_file):
        """Should persist system prompt across manager instances."""
        custom_prompt = "Custom prompt that persists"

        # First manager sets the prompt
        manager1 = UserSettingsManager(settings_file=temp_settings_file)
        manager1.set_system_prompt(custom_prompt)

        # Second manager should read the same prompt
        manager2 = UserSettingsManager(settings_file=temp_settings_file)
        assert manager2.get_system_prompt() == custom_prompt


class TestDashboardSettingsPersistence:
    """Test dashboard settings (provider, model, temperature, max_tokens)."""

    def test_get_default_provider(self, settings_manager):
        """Should return default provider."""
        provider = settings_manager.get_default_provider()
        assert provider is not None

    def test_set_and_get_provider(self, settings_manager):
        """Should persist and retrieve provider setting."""
        settings_manager.set_default_provider('anthropic')
        assert settings_manager.get_default_provider() == 'anthropic'

    def test_set_and_get_model(self, settings_manager):
        """Should persist and retrieve model setting."""
        settings_manager.set_default_model('claude-3-5-sonnet-20241022')
        assert settings_manager.get_default_model() == 'claude-3-5-sonnet-20241022'

    def test_set_and_get_temperature(self, settings_manager):
        """Should persist and retrieve temperature setting."""
        settings_manager.set_temperature(0.5)
        assert settings_manager.get_temperature() == 0.5

    def test_set_and_get_max_tokens(self, settings_manager):
        """Should persist and retrieve max_tokens setting."""
        settings_manager.set_max_tokens(4096)
        assert settings_manager.get_max_tokens() == 4096

    def test_all_dashboard_settings_persist_together(self, temp_settings_file):
        """Should persist all dashboard settings across reloads."""
        # Set all settings
        manager1 = UserSettingsManager(settings_file=temp_settings_file)
        manager1.set_default_provider('google')
        manager1.set_default_model('gemini-2.0-flash')
        manager1.set_temperature(0.3)
        manager1.set_max_tokens(3000)

        # Verify with new manager instance
        manager2 = UserSettingsManager(settings_file=temp_settings_file)
        assert manager2.get_default_provider() == 'google'
        assert manager2.get_default_model() == 'gemini-2.0-flash'
        assert manager2.get_temperature() == 0.3
        assert manager2.get_max_tokens() == 3000


class TestBulkSettingsOperations:
    """Test bulk settings operations."""

    def test_get_all_settings(self, settings_manager):
        """Should return all settings as dictionary."""
        settings_manager.set_default_provider('ollama')
        settings_manager.set_temperature(1.0)

        all_settings = settings_manager.get_all_settings()

        assert isinstance(all_settings, dict)
        assert all_settings['default_provider'] == 'ollama'
        assert all_settings['temperature'] == 1.0

    def test_update_settings_bulk(self, settings_manager):
        """Should update multiple settings at once."""
        updates = {
            'default_provider': 'anthropic',
            'default_model': 'claude-opus-4-20250514',
            'temperature': 0.8,
            'max_tokens': 8000
        }

        settings_manager.update_settings(updates)

        assert settings_manager.get_default_provider() == 'anthropic'
        assert settings_manager.get_default_model() == 'claude-opus-4-20250514'
        assert settings_manager.get_temperature() == 0.8
        assert settings_manager.get_max_tokens() == 8000


class TestSettingsEdgeCases:
    """Test edge cases and error handling."""

    def test_handles_corrupted_file(self, temp_settings_file):
        """Should handle corrupted settings file gracefully."""
        # Corrupt the file
        with open(temp_settings_file, 'w') as f:
            f.write("not valid json {{{")

        # Should not crash
        manager = UserSettingsManager(settings_file=temp_settings_file)
        # Should return default values
        prompt = manager.get_system_prompt()
        assert prompt is not None

    def test_handles_empty_file(self, temp_settings_file):
        """Should handle empty settings file."""
        with open(temp_settings_file, 'w') as f:
            f.write("")

        manager = UserSettingsManager(settings_file=temp_settings_file)
        # Should return defaults without crashing
        assert manager.get_default_provider() is not None

    def test_preserves_extra_settings_on_update(self, settings_manager):
        """Should preserve custom settings when updating known settings."""
        # Add a custom setting
        settings = settings_manager.get_all_settings()
        settings['custom_field'] = 'custom_value'
        settings_manager.update_settings(settings)

        # Update a standard setting
        settings_manager.set_temperature(0.9)

        # Custom field should still exist
        all_settings = settings_manager.get_all_settings()
        assert all_settings.get('custom_field') == 'custom_value'
        assert all_settings['temperature'] == 0.9
