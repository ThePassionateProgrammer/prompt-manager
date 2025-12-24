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
