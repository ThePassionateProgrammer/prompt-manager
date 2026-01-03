"""
User Settings Manager for persisting application preferences.

Handles storage and retrieval of user settings including:
- System prompt
- Default provider and model
- Temperature and max tokens preferences
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional


class UserSettingsManager:
    """Manages persistent user settings stored in JSON file."""

    def __init__(self, settings_file: Path = None):
        if settings_file is None:
            settings_file = Path("settings/user_settings.json")

        self.settings_file = settings_file
        self._ensure_settings_file_exists()

    def _ensure_settings_file_exists(self):
        """Create settings file with defaults if it doesn't exist."""
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.settings_file.exists():
            default_settings = {
                "system_prompt": "You are a helpful AI assistant.",
                "default_provider": "openai",
                "default_model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 2000
            }
            self._save_settings(default_settings)

    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from JSON file."""
        try:
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_settings(self, settings: Dict[str, Any]):
        """Save settings to JSON file."""
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=2)

    def get_system_prompt(self) -> str:
        """Get stored system prompt."""
        settings = self._load_settings()
        return settings.get("system_prompt", "You are a helpful AI assistant.")

    def set_system_prompt(self, prompt: str):
        """Save system prompt."""
        settings = self._load_settings()
        settings["system_prompt"] = prompt
        self._save_settings(settings)

    def get_default_provider(self) -> str:
        """Get default LLM provider."""
        settings = self._load_settings()
        return settings.get("default_provider", "openai")

    def set_default_provider(self, provider: str):
        """Save default provider."""
        settings = self._load_settings()
        settings["default_provider"] = provider
        self._save_settings(settings)

    def get_default_model(self) -> str:
        """Get default model."""
        settings = self._load_settings()
        return settings.get("default_model", "gpt-3.5-turbo")

    def set_default_model(self, model: str):
        """Save default model."""
        settings = self._load_settings()
        settings["default_model"] = model
        self._save_settings(settings)

    def get_temperature(self) -> float:
        """Get default temperature."""
        settings = self._load_settings()
        return settings.get("temperature", 0.7)

    def set_temperature(self, temperature: float):
        """Save temperature preference."""
        settings = self._load_settings()
        settings["temperature"] = temperature
        self._save_settings(settings)

    def get_max_tokens(self) -> int:
        """Get default max tokens."""
        settings = self._load_settings()
        return settings.get("max_tokens", 2000)

    def set_max_tokens(self, max_tokens: int):
        """Save max tokens preference."""
        settings = self._load_settings()
        settings["max_tokens"] = max_tokens
        self._save_settings(settings)

    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings as dictionary."""
        return self._load_settings()

    def update_settings(self, updates: Dict[str, Any]):
        """Update multiple settings at once."""
        settings = self._load_settings()
        settings.update(updates)
        self._save_settings(settings)
