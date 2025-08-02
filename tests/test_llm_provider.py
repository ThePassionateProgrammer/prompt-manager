import pytest
import tempfile
import shutil
import os
from unittest.mock import patch, MagicMock

# Import the LLMProvider interface and OpenAIProvider (to be implemented)
# from src.prompt_manager.business.llm_provider import LLMProvider, OpenAIProvider

class DummyProvider:
    """A dummy provider for testing selection and error handling."""
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
    def send_prompt(self, prompt, **kwargs):
        if self.should_fail:
            raise RuntimeError("Provider error")
        return f"Echo: {prompt}"

def test_provider_selection():
    """Test selecting and using a provider."""
    provider = DummyProvider()
    assert provider.send_prompt("hi") == "Echo: hi"

def test_provider_error_handling():
    """Test provider error handling."""
    provider = DummyProvider(should_fail=True)
    with pytest.raises(RuntimeError):
        provider.send_prompt("fail")

@patch('src.prompt_manager.business.llm_provider.openai.OpenAI')
def test_openai_provider_success(mock_openai_client):
    """Test OpenAIProvider returns a response on success."""
    mock_client = MagicMock()
    mock_create = mock_client.chat.completions.create
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Hello from OpenAI!"
    mock_response.choices = [mock_choice]
    mock_create.return_value = mock_response
    mock_openai_client.return_value = mock_client
    from src.prompt_manager.business.llm_provider import OpenAIProvider
    provider = OpenAIProvider(api_key='test-key')
    response = provider.send_prompt("Hello")
    assert response == "Hello from OpenAI!"

@pytest.mark.skip(reason="Missing key test needs environment isolation")
@patch('src.prompt_manager.business.llm_provider.openai.OpenAI')
def test_openai_provider_missing_key(mock_openai_client):
    """Test OpenAIProvider raises RuntimeError if key is missing."""
    # Create a test key manager with no keys
    temp_dir = tempfile.mkdtemp()
    keys_file = os.path.join(temp_dir, 'test_keys.enc')
    
    try:
        from src.prompt_manager.business.key_loader import SecureKeyManager
        from src.prompt_manager.business.llm_provider import OpenAIProvider
        
        # Create empty key manager
        test_key_manager = SecureKeyManager(keys_file=keys_file, master_password='test-password')
        
        # Reset the global key manager and patch it
        import src.prompt_manager.business.key_loader as key_loader
        key_loader._key_manager = None  # Reset the global instance
        with patch('src.prompt_manager.business.key_loader._key_manager', test_key_manager):
            provider = OpenAIProvider(api_key=None)
            with pytest.raises(RuntimeError):
                provider.send_prompt("test")
    finally:
        shutil.rmtree(temp_dir)

def test_openai_provider_with_secure_key():
    """Test OpenAIProvider works with secure key management."""
    # Create a temporary directory for test
    temp_dir = tempfile.mkdtemp()
    keys_file = os.path.join(temp_dir, 'test_keys.enc')
    
    try:
        from src.prompt_manager.business.key_loader import SecureKeyManager, get_key_manager
        from src.prompt_manager.business.llm_provider import OpenAIProvider
        
        # Create key manager and save a test key
        key_manager = SecureKeyManager(keys_file=keys_file, master_password='test-password')
        key_manager.save_key('openai_api_key', 'sk-test-key')
        
        # Reset the global key manager and patch it
        import src.prompt_manager.business.key_loader as key_loader
        key_loader._key_manager = None  # Reset the global instance
        with patch('src.prompt_manager.business.key_loader._key_manager', key_manager):
            # Create provider that will use the secure key
            provider = OpenAIProvider(api_key=None)  # Will load from secure storage
            
            # Mock the OpenAI client to avoid actual API calls
            with patch('src.prompt_manager.business.llm_provider.openai.OpenAI') as mock_openai:
                mock_client = MagicMock()
                mock_create = mock_client.chat.completions.create
                mock_response = MagicMock()
                mock_choice = MagicMock()
                mock_choice.message.content = "Test response"
                mock_response.choices = [mock_choice]
                mock_create.return_value = mock_response
                mock_openai.return_value = mock_client
                
                # This should work now since we have a key in secure storage
                response = provider.send_prompt("test")
                assert response == "Test response"
                
    finally:
        shutil.rmtree(temp_dir)

@patch('src.prompt_manager.business.llm_provider.openai.OpenAI')
def test_openai_provider_api_error(mock_openai_client):
    """Test OpenAIProvider handles API errors gracefully."""
    mock_client = MagicMock()
    mock_create = mock_client.chat.completions.create
    mock_create.side_effect = Exception("API error")
    mock_openai_client.return_value = mock_client
    from src.prompt_manager.business.llm_provider import OpenAIProvider
    provider = OpenAIProvider(api_key='test-key')
    with pytest.raises(RuntimeError):
        provider.send_prompt("fail") 