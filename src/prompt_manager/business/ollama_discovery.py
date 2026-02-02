"""
Ollama model discovery service.

Discovers available and downloaded Ollama models.
"""
import ollama
from typing import List, Dict, Any
from ..domain.ollama_model import OllamaModel


class OllamaDiscovery:
    """Service for discovering Ollama models.

    Queries local Ollama server for available models.
    """

    def __init__(self, base_url: str = "http://localhost:11434"):
        """Initialize discovery service.

        Args:
            base_url: Ollama server URL (default: http://localhost:11434)
        """
        self.base_url = base_url

    def list_downloaded_models(self) -> List[OllamaModel]:
        """List all models downloaded on local Ollama server.

        Returns:
            List of OllamaModel objects for each downloaded model
        """
        client = ollama.Client(host=self.base_url)
        response = client.list()

        models = []
        # Ollama client returns ListResponse object with .models attribute
        for model_obj in response.models:
            # Extract metadata from Ollama API response
            size_bytes = getattr(model_obj, 'size', 0)
            family = getattr(model_obj.details, 'family', '') if hasattr(model_obj, 'details') else ''
            parameter_size = getattr(model_obj.details, 'parameter_size', '') if hasattr(model_obj, 'details') else ''

            model = OllamaModel(
                model_obj.model,
                size_bytes=size_bytes,
                family=family,
                parameter_size=parameter_size
            )
            models.append(model)

        return models

    def is_server_running(self) -> bool:
        """Check if Ollama server is running and accessible.

        Returns:
            True if server responds, False otherwise
        """
        try:
            client = ollama.Client(host=self.base_url)
            client.list()
            return True
        except Exception:
            return False

    def pull_model(self, model_name: str) -> Dict[str, Any]:
        """Pull/download a model from Ollama library.

        Args:
            model_name: Model to download (e.g., 'gemma3:4b', 'llama3:8b')

        Returns:
            Dict with 'success' boolean and optional 'error' message
        """
        try:
            client = ollama.Client(host=self.base_url)
            # Stream the pull to handle progress (consumes iterator)
            for _ in client.pull(model_name, stream=True):
                pass
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def delete_model(self, model_name: str) -> Dict[str, Any]:
        """Delete a downloaded model.

        Args:
            model_name: Model to delete (e.g., 'gemma3:4b')

        Returns:
            Dict with 'success' boolean and optional 'error' message
        """
        try:
            client = ollama.Client(host=self.base_url)
            client.delete(model_name)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
