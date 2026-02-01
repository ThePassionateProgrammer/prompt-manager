"""
Feature Flags - Control which features are enabled.

Simple feature flag system for hiding incomplete features.
Flags can be set via environment variables or config file.
"""
import os
import json
from pathlib import Path

# Default feature flags - False means hidden from users
DEFAULT_FLAGS = {
    'TEMPLATE_BUILDER': False,  # Template builder UI
    'CUSTOM_COMBO_BOX': False,  # Custom combo box features
    'LINKAGES': False,          # Linkage system
    'MEMORY_CARDS': False,      # Memory card system (future)
}

# Config file location
CONFIG_FILE = Path(__file__).parent.parent.parent.parent / 'settings' / 'feature_flags.json'


class FeatureFlags:
    """Manages feature flags for the application.

    Flags are loaded in this priority order:
    1. Environment variables (PROMPT_MANAGER_FLAG_<NAME>)
    2. Config file (settings/feature_flags.json)
    3. Default values (all experimental features disabled)
    """

    _instance = None
    _flags = None

    def __new__(cls):
        """Singleton pattern - only one instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_flags()
        return cls._instance

    def _load_flags(self):
        """Load flags from environment and config file."""
        self._flags = DEFAULT_FLAGS.copy()

        # Load from config file if exists
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    file_flags = json.load(f)
                    for key, value in file_flags.items():
                        if key in self._flags:
                            self._flags[key] = bool(value)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[FeatureFlags] Warning: Could not load config file: {e}")

        # Environment variables override config file
        for key in self._flags:
            env_var = f"PROMPT_MANAGER_FLAG_{key}"
            env_value = os.environ.get(env_var)
            if env_value is not None:
                self._flags[key] = env_value.lower() in ('true', '1', 'yes', 'on')

    def is_enabled(self, flag_name: str) -> bool:
        """Check if a feature flag is enabled.

        Args:
            flag_name: Name of the feature flag (e.g., 'TEMPLATE_BUILDER')

        Returns:
            True if enabled, False otherwise
        """
        return self._flags.get(flag_name, False)

    def get_all_flags(self) -> dict:
        """Get all feature flags and their current values.

        Returns:
            Dictionary of flag names to boolean values
        """
        return self._flags.copy()

    def reload(self):
        """Reload flags from config file and environment."""
        self._load_flags()


# Convenience functions for easy access
def is_enabled(flag_name: str) -> bool:
    """Check if a feature flag is enabled."""
    return FeatureFlags().is_enabled(flag_name)


def get_all_flags() -> dict:
    """Get all feature flags."""
    return FeatureFlags().get_all_flags()


# Specific flag checks for common use
def template_builder_enabled() -> bool:
    """Check if template builder is enabled."""
    return is_enabled('TEMPLATE_BUILDER')


def custom_combo_enabled() -> bool:
    """Check if custom combo box is enabled."""
    return is_enabled('CUSTOM_COMBO_BOX')


def linkages_enabled() -> bool:
    """Check if linkages are enabled."""
    return is_enabled('LINKAGES')
