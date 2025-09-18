"""
Integration layer for linking the linkage domain model with the frontend.

This module provides a clean interface between the domain model and the
JavaScript frontend, handling serialization and deserialization.
"""

from typing import Dict, List, Any
from src.prompt_manager.domain.linkage_manager import LinkageManager


class LinkageIntegrationService:
    """
    Service for integrating the linkage domain model with the frontend.
    
    This class handles the translation between the domain model and the
    JavaScript objects used in the frontend.
    """
    
    def __init__(self):
        self.linkage_manager = LinkageManager()
    
    def register_combo_boxes(self, combo_box_tags: List[str]) -> None:
        """Register combo boxes in their hierarchical order."""
        for i, tag in enumerate(combo_box_tags):
            self.linkage_manager.register_combo_box(tag, i)
    
    def create_linkage_from_frontend(self, parent_tag: str, child_tag: str, option: str) -> None:
        """Create a linkage from frontend data."""
        self.linkage_manager.create_linkage(parent_tag, child_tag, option)
    
    def update_selection_from_frontend(self, tag: str, selected_option: str) -> None:
        """Update selection from frontend data."""
        self.linkage_manager.update_selection(tag, selected_option)
    
    def get_restoration_data(self, parent_tag: str) -> Dict[str, Any]:
        """
        Get data needed for restoration when a parent selection changes.
        
        Returns:
            Dict containing:
            - affected_combo_boxes: List of combo box tags that need clearing
            - restoration_chain: List of (parent, child) tuples for restoration
            - linkage_data: Linkage data for JavaScript
        """
        affected_combo_boxes = self.linkage_manager.get_affected_combo_boxes(parent_tag)
        restoration_chain = self.linkage_manager.get_restoration_chain(parent_tag)
        linkage_data = self.linkage_manager.get_linkage_data_for_js()
        
        return {
            'affected_combo_boxes': affected_combo_boxes,
            'restoration_chain': restoration_chain,
            'linkage_data': linkage_data
        }
    
    def get_frontend_data(self) -> Dict[str, Any]:
        """Get all data needed by the frontend."""
        return {
            'linkage_data': self.linkage_manager.get_linkage_data_for_js(),
            'current_selections': self.linkage_manager.get_current_selections_for_js()
        }
    
    def validate_integrity(self) -> List[str]:
        """Validate the integrity of all linkage data."""
        return self.linkage_manager.validate_linkage_integrity()
