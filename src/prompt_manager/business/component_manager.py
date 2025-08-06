import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class ComponentManager:
    """Manage component data with parent-child relationships."""
    
    def __init__(self, components_file: Optional[Path] = None):
        """
        Initialize the component manager.
        
        Args:
            components_file: Path to JSON file containing component data
        """
        if components_file is None:
            components_file = Path(__file__).parent.parent / "data" / "components.json"
        
        self.components_file = Path(components_file)
        self.components_data = self._load_components()
    
    def _load_components(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load components from JSON file."""
        try:
            with open(self.components_file, 'r') as f:
                data = json.load(f)
                return data.get("components", {})
        except FileNotFoundError:
            raise FileNotFoundError(f"Components file not found: {self.components_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in components file: {e}")
    
    def get_all_components(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all components organized by tag."""
        return self.components_data
    
    def get_root_components(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get root components (those without parents)."""
        root_components = {}
        
        for tag, components in self.components_data.items():
            root_items = [comp for comp in components if "parent" not in comp]
            if root_items:
                root_components[tag] = root_items
        
        return root_components
    
    def get_child_components(self, tag: str, parent_label: str) -> List[Dict[str, Any]]:
        """
        Get child components for a specific parent.
        
        Args:
            tag: The tag name (e.g., "What", "Why")
            parent_label: The label of the parent component
            
        Returns:
            List of child components for the specified parent
        """
        if tag not in self.components_data:
            return []
        
        children = [
            comp for comp in self.components_data[tag]
            if comp.get("parent") == parent_label
        ]
        
        return children
    
    def get_component_options(self, tag: str, parent_label: Optional[str] = None) -> List[str]:
        """
        Get available options for a component tag.
        
        Args:
            tag: The tag name
            parent_label: Optional parent label for filtering
            
        Returns:
            List of available option labels
        """
        if tag not in self.components_data:
            return []
        
        if parent_label is None:
            # Return root components (no parent)
            options = [
                comp["label"] for comp in self.components_data[tag]
                if "parent" not in comp
            ]
        else:
            # Return child components for specific parent
            options = [
                comp["label"] for comp in self.components_data[tag]
                if comp.get("parent") == parent_label
            ]
        
        return options 