"""
Ollama model discovery service.

Discovers available and downloaded Ollama models.
"""
import ollama
from typing import List
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
        for model_data in response.get('models', []):
            model = OllamaModel(model_data['name'])
            models.append(model)

        return models
