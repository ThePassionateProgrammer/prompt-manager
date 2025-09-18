"""
Domain model for managing hierarchical linkages between combo boxes.

This module provides a clean, testable domain model for managing the complex
relationships between combo boxes in the Template Builder.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field


@dataclass
class LinkageRule:
    """Represents a single linkage rule between parent and child combo boxes."""
    parent_tag: str
    child_tag: str
    linked_options: List[str] = field(default_factory=list)
    
    def add_linked_option(self, option: str) -> None:
        """Add an option to this linkage rule if not already present."""
        if option not in self.linked_options:
            self.linked_options.append(option)
    
    def remove_linked_option(self, option: str) -> None:
        """Remove an option from this linkage rule."""
        if option in self.linked_options:
            self.linked_options.remove(option)
    
    def has_linked_options(self) -> bool:
        """Check if this linkage rule has any linked options."""
        return len(self.linked_options) > 0


@dataclass
class ComboBoxState:
    """Represents the current state of a combo box."""
    tag: str
    selected_option: Optional[str] = None
    available_options: List[str] = field(default_factory=list)
    
    def is_selected(self) -> bool:
        """Check if this combo box has a selection."""
        return self.selected_option is not None and self.selected_option != ""
    
    def clear_selection(self) -> None:
        """Clear the current selection."""
        self.selected_option = None


class LinkageManager:
    """
    Manages hierarchical linkages between combo boxes.
    
    This class encapsulates all the complex logic for managing parent-child
    relationships, option restoration, and cascading updates.
    """
    
    def __init__(self):
        self.linkage_rules: Dict[str, Dict[str, LinkageRule]] = {}
        self.combo_box_states: Dict[str, ComboBoxState] = {}
        self.combo_box_order: List[str] = []
    
    def register_combo_box(self, tag: str, position: int) -> None:
        """Register a combo box with its position in the hierarchy."""
        self.combo_box_states[tag] = ComboBoxState(tag=tag)
        # Insert at the correct position
        if position >= len(self.combo_box_order):
            self.combo_box_order.extend([None] * (position - len(self.combo_box_order) + 1))
        self.combo_box_order[position] = tag
    
    def create_linkage(self, parent_tag: str, child_tag: str, option: str) -> None:
        """
        Create a linkage between parent and child combo boxes for a specific option.
        
        Args:
            parent_tag: Tag of the parent combo box
            child_tag: Tag of the child combo box  
            option: The option value that creates the linkage
        """
        if parent_tag not in self.linkage_rules:
            self.linkage_rules[parent_tag] = {}
        
        if child_tag not in self.linkage_rules[parent_tag]:
            self.linkage_rules[parent_tag][child_tag] = LinkageRule(
                parent_tag=parent_tag,
                child_tag=child_tag
            )
        
        self.linkage_rules[parent_tag][child_tag].add_linked_option(option)
    
    def get_linked_options(self, parent_tag: str, child_tag: str) -> List[str]:
        """Get the linked options for a specific parent-child relationship."""
        if parent_tag in self.linkage_rules and child_tag in self.linkage_rules[parent_tag]:
            return self.linkage_rules[parent_tag][child_tag].linked_options.copy()
        return []
    
    def update_selection(self, tag: str, selected_option: str) -> None:
        """Update the selection for a specific combo box."""
        if tag in self.combo_box_states:
            self.combo_box_states[tag].selected_option = selected_option
    
    def get_affected_combo_boxes(self, parent_tag: str) -> List[str]:
        """
        Get all combo boxes that should be affected when parent_tag changes.
        
        Returns combo boxes in order from immediate children to descendants.
        """
        parent_position = self.combo_box_order.index(parent_tag) if parent_tag in self.combo_box_order else -1
        if parent_position == -1:
            return []
        
        # Return all combo boxes that come after this parent
        return [tag for tag in self.combo_box_order[parent_position + 1:] if tag is not None]
    
    def should_restore_linkages(self, parent_tag: str, child_tag: str) -> bool:
        """Check if linkages should be restored for a parent-child relationship."""
        return (parent_tag in self.linkage_rules and 
                child_tag in self.linkage_rules[parent_tag] and
                self.linkage_rules[parent_tag][child_tag].has_linked_options())
    
    def get_restoration_chain(self, parent_tag: str) -> List[tuple[str, str]]:
        """
        Get the chain of parent-child relationships that need restoration.
        
        Returns a list of (parent_tag, child_tag) tuples in restoration order.
        """
        restoration_chain = []
        affected_boxes = self.get_affected_combo_boxes(parent_tag)
        
        for child_tag in affected_boxes:
            if self.should_restore_linkages(parent_tag, child_tag):
                restoration_chain.append((parent_tag, child_tag))
        
        return restoration_chain
    
    def clear_subsequent_selections(self, parent_tag: str) -> None:
        """Clear selections for all combo boxes that come after the parent."""
        affected_boxes = self.get_affected_combo_boxes(parent_tag)
        for tag in affected_boxes:
            if tag in self.combo_box_states:
                self.combo_box_states[tag].clear_selection()
    
    def get_linkage_data_for_js(self) -> Dict:
        """
        Get linkage data in the format expected by JavaScript.
        
        Returns a dictionary that can be serialized to JSON for use in the frontend.
        """
        js_linkage_data = {}
        for parent_tag, child_rules in self.linkage_rules.items():
            js_linkage_data[parent_tag] = {}
            for child_tag, rule in child_rules.items():
                js_linkage_data[parent_tag][child_tag] = rule.linked_options.copy()
        return js_linkage_data
    
    def get_current_selections_for_js(self) -> Dict:
        """Get current selections in the format expected by JavaScript."""
        js_selections = {}
        for tag, state in self.combo_box_states.items():
            if state.is_selected():
                js_selections[tag] = state.selected_option
        return js_selections
    
    def validate_linkage_integrity(self) -> List[str]:
        """
        Validate the integrity of all linkage rules.
        
        Returns a list of validation error messages.
        """
        errors = []
        
        # Check that all referenced combo boxes exist
        for parent_tag, child_rules in self.linkage_rules.items():
            if parent_tag not in self.combo_box_states:
                errors.append(f"Parent combo box '{parent_tag}' not registered")
            
            for child_tag, rule in child_rules.items():
                if child_tag not in self.combo_box_states:
                    errors.append(f"Child combo box '{child_tag}' not registered")
        
        return errors
