"""
Tests for Dashboard Settings API endpoints.

Test-first development: API integration tests for settings persistence.
"""
import pytest
import json
import tempfile
from pathlib import Path
from flask import Flask
from routes.dashboard import dashboard_bp
from src.prompt_manager.business.user_settings_manager import UserSettingsManager


@pytest.fixture
def app(tmp_path):
    """Create Flask test app with isolated settings."""
    app = Flask(__name__)
    app.config['TESTING'] = True

    # Use isolated settings file for tests
    settings_file = tmp_path / "test_settings.json"
    test_settings_manager = UserSettingsManager(settings_file=settings_file)

    # Monkey-patch the settings_manager in the dashboard module
    import routes.dashboard as dashboard_module
    original_manager = dashboard_module.settings_manager
    dashboard_module.settings_manager = test_settings_manager

    app.register_blueprint(dashboard_bp)

    yield app

    # Restore original manager
    dashboard_module.settings_manager = original_manager


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestDashboardSettingsAPI:
    """Test /api/settings/dashboard endpoint."""

    def test_get_dashboard_settings(self, client):
        """GET should return current dashboard settings."""
        response = client.get('/api/settings/dashboard')

        assert response.status_code == 200
        data = response.get_json()
        assert 'provider' in data
        assert 'model' in data
        assert 'temperature' in data
        assert 'max_tokens' in data

    def test_post_dashboard_settings(self, client):
        """POST should save dashboard settings."""
        settings = {
            'provider': 'anthropic',
            'model': 'claude-3-5-sonnet-20241022',
            'temperature': 0.5,
            'max_tokens': 4096
        }

        response = client.post(
            '/api/settings/dashboard',
            json=settings,
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Dashboard settings saved successfully'

    def test_dashboard_settings_persist(self, client):
        """Settings should persist across requests."""
        # Save settings
        settings = {
            'provider': 'google',
            'model': 'gemini-2.0-flash',
            'temperature': 0.3,
            'max_tokens': 3000
        }
        client.post('/api/settings/dashboard', json=settings)

        # Retrieve settings
        response = client.get('/api/settings/dashboard')
        data = response.get_json()

        assert data['provider'] == 'google'
        assert data['model'] == 'gemini-2.0-flash'
        assert data['temperature'] == 0.3
        assert data['max_tokens'] == 3000

    def test_partial_update_preserves_other_settings(self, client):
        """Partial update should not overwrite other settings."""
        # Set all settings
        client.post('/api/settings/dashboard', json={
            'provider': 'anthropic',
            'model': 'claude-opus',
            'temperature': 0.8,
            'max_tokens': 2000
        })

        # Update only temperature
        client.post('/api/settings/dashboard', json={
            'temperature': 1.0
        })

        # Check other settings preserved
        response = client.get('/api/settings/dashboard')
        data = response.get_json()

        assert data['provider'] == 'anthropic'
        assert data['model'] == 'claude-opus'
        assert data['temperature'] == 1.0
        assert data['max_tokens'] == 2000


class TestSystemPromptAPI:
    """Test /api/settings/system-prompt endpoint."""

    def test_get_system_prompt(self, client):
        """GET should return current system prompt."""
        response = client.get('/api/settings/system-prompt')

        assert response.status_code == 200
        data = response.get_json()
        assert 'prompt' in data
        assert len(data['prompt']) > 0

    def test_set_system_prompt(self, client):
        """POST should save system prompt."""
        custom_prompt = "You are a specialized Python developer assistant."

        response = client.post(
            '/api/settings/system-prompt',
            json={'prompt': custom_prompt},
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['prompt'] == custom_prompt

    def test_system_prompt_persists(self, client):
        """System prompt should persist across requests."""
        custom_prompt = "You are a creative writing assistant."

        # Save prompt
        client.post('/api/settings/system-prompt', json={'prompt': custom_prompt})

        # Retrieve prompt
        response = client.get('/api/settings/system-prompt')
        data = response.get_json()

        assert data['prompt'] == custom_prompt

    def test_set_system_prompt_requires_prompt(self, client):
        """POST without prompt should return error."""
        response = client.post(
            '/api/settings/system-prompt',
            json={},
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_get_default_system_prompt(self, client):
        """Should return the default system prompt."""
        response = client.get('/api/settings/system-prompt/default')

        assert response.status_code == 200
        data = response.get_json()
        assert 'prompt' in data
        assert len(data['prompt']) > 0


class TestHandsFreeSettingsAPI:
    """Test /api/settings/hands-free endpoint."""

    def test_get_hands_free_settings(self, client):
        """GET should return hands-free settings."""
        response = client.get('/api/settings/hands-free')

        assert response.status_code == 200
        data = response.get_json()
        assert 'wake_words' in data
        assert 'sleep_words' in data
        assert 'auto_send_timeout' in data

    def test_set_hands_free_timeout(self, client):
        """POST should save auto_send_timeout."""
        response = client.post(
            '/api/settings/hands-free',
            json={'auto_send_timeout': 8},
            content_type='application/json'
        )

        assert response.status_code == 200

        # Verify it persisted
        response = client.get('/api/settings/hands-free')
        data = response.get_json()
        assert data['auto_send_timeout'] == 8

    def test_default_wake_words_include_variations(self, client):
        """Default wake words should include Ember variations."""
        response = client.get('/api/settings/hands-free')
        data = response.get_json()

        wake_words = data['wake_words']
        # Should include both "amber" and "ember" variations
        assert any('amber' in word.lower() for word in wake_words)
        assert any('ember' in word.lower() for word in wake_words)


class TestVoiceSettingsAPI:
    """Test /api/settings/voice endpoint for persistent voice controls."""

    def test_get_voice_settings_returns_defaults(self, client):
        """GET should return default voice settings."""
        response = client.get('/api/settings/voice')

        assert response.status_code == 200
        data = response.get_json()
        assert 'voice_name' in data
        assert 'rate' in data
        assert 'pitch' in data
        assert 'auto_send_timeout' in data

    def test_get_voice_settings_default_values(self, client):
        """Default voice settings should have sensible values."""
        response = client.get('/api/settings/voice')
        data = response.get_json()

        assert data['rate'] == 1.0
        assert data['pitch'] == 1.0
        assert data['auto_send_timeout'] == 5
        assert data['voice_name'] == ''  # No voice selected by default

    def test_save_voice_settings(self, client):
        """POST should save voice settings."""
        settings = {
            'voice_name': 'Samantha',
            'rate': 1.2,
            'pitch': 0.8,
            'auto_send_timeout': 7
        }

        response = client.post('/api/settings/voice', json=settings)

        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Voice settings saved successfully'

    def test_voice_settings_persist(self, client):
        """Voice settings should persist across requests."""
        settings = {
            'voice_name': 'Daniel',
            'rate': 1.5,
            'pitch': 0.9,
            'auto_send_timeout': 3
        }
        client.post('/api/settings/voice', json=settings)

        response = client.get('/api/settings/voice')
        data = response.get_json()

        assert data['voice_name'] == 'Daniel'
        assert data['rate'] == 1.5
        assert data['pitch'] == 0.9
        assert data['auto_send_timeout'] == 3

    def test_partial_voice_settings_update(self, client):
        """Should update only provided fields, preserving others."""
        # Set initial values
        client.post('/api/settings/voice', json={
            'voice_name': 'Samantha',
            'rate': 1.2,
            'pitch': 0.8,
            'auto_send_timeout': 7
        })

        # Update only rate
        client.post('/api/settings/voice', json={'rate': 1.8})

        response = client.get('/api/settings/voice')
        data = response.get_json()

        assert data['voice_name'] == 'Samantha'
        assert data['rate'] == 1.8
        assert data['pitch'] == 0.8
        assert data['auto_send_timeout'] == 7
