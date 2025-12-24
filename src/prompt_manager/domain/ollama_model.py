"""
OllamaModel domain model.

Pure business logic for Ollama model representation with zero dependencies.
"""


class OllamaModel:
    """Represents an Ollama model with name and tag.

    Ollama models follow the pattern: name:tag (e.g., gemma3:4b)
    This is pure domain logic - no dependencies on Ollama client or infrastructure.
    """

    def __init__(
        self,
        full_name: str,
        size_bytes: int = 0,
        family: str = "",
        parameter_size: str = ""
    ):
        """Parse Ollama model name into components.

        Args:
            full_name: Full model identifier (e.g., "gemma3:4b")
            size_bytes: Model size in bytes (default: 0)
            family: Model family (e.g., "gemma3", "llama")
            parameter_size: Parameter count (e.g., "4.3B", "8.0B")

        Raises:
            ValueError: If model name is empty or invalid
        """
        if not full_name or not full_name.strip():
            raise ValueError("Model name cannot be empty")

        parts = full_name.split(':')
        self.name = parts[0]
        self.tag = parts[1] if len(parts) > 1 else 'latest'
        self.full_name = full_name
        self.size_bytes = size_bytes
        self.family = family
        self.parameter_size = parameter_size

    def size_gb(self) -> float:
        """Convert bytes to gigabytes for display.

        Returns:
            Size in GB, rounded to 1 decimal place
        """
        return round(self.size_bytes / (1024**3), 1)

    def size_display(self) -> str:
        """Human-readable size string.

        Returns:
            Formatted string like "3.1 GB"
        """
        return f"{self.size_gb()} GB"

    def is_lightweight(self) -> bool:
        """Check if model can run on modest hardware.

        Models under 5GB are considered lightweight.

        Returns:
            True if model is under 5GB, False otherwise
        """
        return self.size_gb() < 5.0

    def to_dict(self) -> dict:
        """Serialize model to dictionary for persistence.

        Returns:
            Dictionary with model name, tag, full_name, and metadata
        """
        return {
            'name': self.name,
            'tag': self.tag,
            'full_name': self.full_name,
            'size_bytes': self.size_bytes,
            'size_display': self.size_display(),
            'family': self.family,
            'parameter_size': self.parameter_size,
            'is_lightweight': self.is_lightweight()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'OllamaModel':
        """Deserialize model from dictionary.

        Args:
            data: Dictionary with model data (must have 'full_name' key)

        Returns:
            OllamaModel instance
        """
        return cls(data['full_name'])
