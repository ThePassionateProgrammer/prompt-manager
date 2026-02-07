import json
from pathlib import Path
from typing import Dict, List, Optional, Any

class PromptBuilder:
    """Business logic for building prompts from pieces."""
    
    def __init__(self, pieces_file: Optional[str] = None):
        """Initialize the prompt builder with pieces data."""
        if pieces_file is None:
            pieces_file = Path(__file__).parent.parent / "data" / "prompt_pieces.json"
        
        self.pieces_file = Path(pieces_file)
        self.pieces_data = self._load_pieces()
    
    def _load_pieces(self) -> Dict[str, Any]:
        """Load prompt pieces from JSON file."""
        try:
            with open(self.pieces_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt pieces file not found: {self.pieces_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in prompt pieces file: {e}")
    
    def get_available_roles(self) -> Dict[str, Dict[str, str]]:
        """Get all available roles organized by category."""
        return self.pieces_data.get("roles", {})
    
    def get_available_voices(self) -> Dict[str, str]:
        """Get all available voices."""
        return self.pieces_data.get("voices", {})
    
    def get_available_contexts(self) -> Dict[str, Dict[str, str]]:
        """Get all available contexts organized by category."""
        return self.pieces_data.get("contexts", {})
    
    def get_available_audiences(self) -> Dict[str, str]:
        """Get all available audiences."""
        return self.pieces_data.get("audiences", {})
    
    def get_available_formats(self) -> Dict[str, str]:
        """Get all available formats."""
        return self.pieces_data.get("formats", {})
    
    def get_available_models(self) -> Dict[str, str]:
        """Get all available models."""
        return self.pieces_data.get("models", {})
    
    def get_role_text(self, category: str, role: str) -> str:
        """Get the text for a specific role."""
        roles = self.get_available_roles()
        if category not in roles:
            raise ValueError(f"Role category '{category}' not found")
        if role not in roles[category]:
            raise ValueError(f"Role '{role}' not found in category '{category}'")
        return roles[category][role]
    
    def get_context_text(self, category: str, context: str) -> str:
        """Get the text for a specific context."""
        contexts = self.get_available_contexts()
        if category not in contexts:
            raise ValueError(f"Context category '{category}' not found")
        if context not in contexts[category]:
            raise ValueError(f"Context '{context}' not found in category '{category}'")
        return contexts[category][context]
    
    def get_voice_text(self, voice: str) -> str:
        """Get the text for a specific voice."""
        voices = self.get_available_voices()
        if voice not in voices:
            raise ValueError(f"Voice '{voice}' not found")
        return voices[voice]
    
    def get_audience_text(self, audience: str) -> str:
        """Get the text for a specific audience."""
        audiences = self.get_available_audiences()
        if audience not in audiences:
            raise ValueError(f"Audience '{audience}' not found")
        return audiences[audience]
    
    def get_format_text(self, format_type: str) -> str:
        """Get the text for a specific format."""
        formats = self.get_available_formats()
        if format_type not in formats:
            raise ValueError(f"Format '{format_type}' not found")
        return formats[format_type]
    
    def get_model_text(self, model: str) -> str:
        """Get the text for a specific model."""
        models = self.get_available_models()
        if model not in models:
            raise ValueError(f"Model '{model}' not found")
        return models[model]
    
    def build_prompt(self, 
                    role_category: Optional[str] = None,
                    role: Optional[str] = None,
                    voice: Optional[str] = None,
                    context_category: Optional[str] = None,
                    context: Optional[str] = None,
                    audience: Optional[str] = None,
                    format_type: Optional[str] = None,
                    custom_text: Optional[str] = None,
                    model: Optional[str] = None,
                    temperature: Optional[float] = None,
                    max_tokens: Optional[int] = None,
                    min_tokens: Optional[int] = None) -> Dict[str, Any]:
        """Build a complete prompt from selected pieces."""
        prompt_parts = []
        
        # Add role if specified
        if role_category and role:
            prompt_parts.append(self.get_role_text(role_category, role))
        
        # Add context if specified
        if context_category and context:
            prompt_parts.append(self.get_context_text(context_category, context))
        
        # Add voice if specified
        if voice:
            prompt_parts.append(self.get_voice_text(voice))
        
        # Add audience if specified
        if audience:
            prompt_parts.append(self.get_audience_text(audience))
        
        # Add format if specified
        if format_type:
            prompt_parts.append(self.get_format_text(format_type))
        
        # Add custom text if provided
        if custom_text:
            prompt_parts.append(custom_text)
        
        # Combine all parts
        if not prompt_parts:
            return {
                "prompt": "",
                "model": model or "gpt-4-turbo",
                "temperature": temperature or 0.7,
                "max_tokens": max_tokens or 1000,
                "min_tokens": min_tokens or 50
            }
        
        result = {
            "prompt": "\n\n".join(prompt_parts),
            "model": model or "gpt-4-turbo",
            "temperature": temperature or 0.7,
            "max_tokens": max_tokens or 1000,
            "min_tokens": min_tokens or 50
        }
        
        return result
    
    def get_prompt_preview(self, **kwargs) -> str:
        """Get a preview of the prompt without building the full version."""
        return self.build_prompt(**kwargs) 