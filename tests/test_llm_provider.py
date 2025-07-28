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

@patch('src.prompt_manager.business.llm_provider.openai.OpenAI')
def test_openai_provider_missing_key(mock_openai_client):
    """Test OpenAIProvider raises ValueError if key is missing."""
    from src.prompt_manager.business.llm_provider import OpenAIProvider
    with pytest.raises(ValueError):
        OpenAIProvider(api_key=None)

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