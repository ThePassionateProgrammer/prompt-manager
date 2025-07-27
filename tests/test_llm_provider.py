import pytest
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
    assert provider.send_prompt("Hello") == "Echo: Hello"

def test_provider_error_handling():
    """Test error handling when provider fails."""
    provider = DummyProvider(should_fail=True)
    with pytest.raises(RuntimeError):
        provider.send_prompt("Hello")

@patch('src.prompt_manager.business.llm_provider.openai')
def test_openai_provider_success(mock_openai):
    """Test OpenAIProvider returns a response on success."""
    # Setup mock
    mock_openai.ChatCompletion.create.return_value = {
        'choices': [{'message': {'content': 'Hello from OpenAI!'}}]
    }
    from src.prompt_manager.business.llm_provider import OpenAIProvider
    provider = OpenAIProvider(api_key='test-key')
    response = provider.send_prompt("Hello")
    assert response == "Hello from OpenAI!"

@patch('src.prompt_manager.business.llm_provider.openai')
def test_openai_provider_missing_key(mock_openai):
    """Test OpenAIProvider raises error if API key is missing."""
    from src.prompt_manager.business.llm_provider import OpenAIProvider
    with pytest.raises(ValueError):
        OpenAIProvider(api_key=None)

@patch('src.prompt_manager.business.llm_provider.openai')
def test_openai_provider_api_error(mock_openai):
    """Test OpenAIProvider handles API errors gracefully."""
    mock_openai.ChatCompletion.create.side_effect = Exception("API error")
    from src.prompt_manager.business.llm_provider import OpenAIProvider
    provider = OpenAIProvider(api_key='test-key')
    with pytest.raises(Exception):
        provider.send_prompt("Hello") 