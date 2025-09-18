"""
Unit tests for the linkage domain model.

These tests focus on behavior and business logic rather than implementation details.
"""

import pytest
from src.prompt_manager.domain.linkage_manager import (
    LinkageManager, LinkageRule, ComboBoxState
)


class TestLinkageRule:
    """Test the LinkageRule domain object."""
    
    def test_create_linkage_rule(self):
        """Test creating a basic linkage rule."""
        rule = LinkageRule(parent_tag="Role", child_tag="What")
        
        assert rule.parent_tag == "Role"
        assert rule.child_tag == "What"
        assert rule.linked_options == []
        assert not rule.has_linked_options()
    
    def test_add_linked_option(self):
        """Test adding linked options."""
        rule = LinkageRule(parent_tag="Role", child_tag="What")
        
        rule.add_linked_option("Write Code")
        assert rule.has_linked_options()
        assert "Write Code" in rule.linked_options
        
        # Adding the same option twice should not duplicate
        rule.add_linked_option("Write Code")
        assert rule.linked_options == ["Write Code"]
    
    def test_remove_linked_option(self):
        """Test removing linked options."""
        rule = LinkageRule(parent_tag="Role", child_tag="What")
        rule.add_linked_option("Write Code")
        rule.add_linked_option("Test Code")
        
        rule.remove_linked_option("Write Code")
        assert "Write Code" not in rule.linked_options
        assert "Test Code" in rule.linked_options
        assert rule.has_linked_options()
        
        # Removing non-existent option should not raise error
        rule.remove_linked_option("Non-existent")
        assert rule.linked_options == ["Test Code"]


class TestComboBoxState:
    """Test the ComboBoxState domain object."""
    
    def test_create_combo_box_state(self):
        """Test creating a combo box state."""
        state = ComboBoxState(tag="Role")
        
        assert state.tag == "Role"
        assert state.selected_option is None
        assert state.available_options == []
        assert not state.is_selected()
    
    def test_selection_state(self):
        """Test selection state management."""
        state = ComboBoxState(tag="Role")
        
        state.selected_option = "Programmer"
        assert state.is_selected()
        assert state.selected_option == "Programmer"
        
        state.clear_selection()
        assert not state.is_selected()
        assert state.selected_option is None
    
    def test_empty_string_not_considered_selected(self):
        """Test that empty string is not considered a valid selection."""
        state = ComboBoxState(tag="Role")
        
        state.selected_option = ""
        assert not state.is_selected()


class TestLinkageManager:
    """Test the LinkageManager domain model."""
    
    def setup_method(self):
        """Set up test environment."""
        self.manager = LinkageManager()
    
    def test_register_combo_boxes(self):
        """Test registering combo boxes in order."""
        self.manager.register_combo_box("Role", 0)
        self.manager.register_combo_box("What", 1)
        self.manager.register_combo_box("Why", 2)
        
        assert "Role" in self.manager.combo_box_states
        assert "What" in self.manager.combo_box_states
        assert "Why" in self.manager.combo_box_states
        assert self.manager.combo_box_order == ["Role", "What", "Why"]
    
    def test_create_linkage(self):
        """Test creating linkages between combo boxes."""
        self.manager.register_combo_box("Role", 0)
        self.manager.register_combo_box("What", 1)
        
        self.manager.create_linkage("Role", "What", "Write Code")
        
        linked_options = self.manager.get_linked_options("Role", "What")
        assert linked_options == ["Write Code"]
    
    def test_create_multiple_linkages_for_same_parent_child(self):
        """Test creating multiple linkages for the same parent-child pair."""
        self.manager.register_combo_box("Role", 0)
        self.manager.register_combo_box("What", 1)
        
        self.manager.create_linkage("Role", "What", "Write Code")
        self.manager.create_linkage("Role", "What", "Test Code")
        
        linked_options = self.manager.get_linked_options("Role", "What")
        assert "Write Code" in linked_options
        assert "Test Code" in linked_options
        assert len(linked_options) == 2
    
    def test_create_linkages_for_different_parents(self):
        """Test creating linkages for different parent selections."""
        self.manager.register_combo_box("Role", 0)
        self.manager.register_combo_box("What", 1)
        
        # Programmer -> Write Code
        self.manager.create_linkage("Role", "What", "Write Code")
        
        # Manager -> Review Code  
        self.manager.create_linkage("Role", "What", "Review Code")
        
        # Note: This test shows the current limitation - we need to track
        # which parent selection each linkage belongs to
        linked_options = self.manager.get_linked_options("Role", "What")
        assert "Write Code" in linked_options
        assert "Review Code" in linked_options
    
    def test_get_affected_combo_boxes(self):
        """Test getting combo boxes affected by parent changes."""
        self.manager.register_combo_box("Role", 0)
        self.manager.register_combo_box("What", 1)
        self.manager.register_combo_box("Why", 2)
        
        affected = self.manager.get_affected_combo_boxes("Role")
        assert affected == ["What", "Why"]
        
        affected = self.manager.get_affected_combo_boxes("What")
        assert affected == ["Why"]
        
        affected = self.manager.get_affected_combo_boxes("Why")
        assert affected == []
    
    def test_update_selection(self):
        """Test updating combo box selections."""
        self.manager.register_combo_box("Role", 0)
        
        self.manager.update_selection("Role", "Programmer")
        
        state = self.manager.combo_box_states["Role"]
        assert state.selected_option == "Programmer"
        assert state.is_selected()
    
    def test_should_restore_linkages(self):
        """Test checking if linkages should be restored."""
        self.manager.register_combo_box("Role", 0)
        self.manager.register_combo_box("What", 1)
        
        # No linkages exist
        assert not self.manager.should_restore_linkages("Role", "What")
        
        # Create linkage
        self.manager.create_linkage("Role", "What", "Write Code")
        assert self.manager.should_restore_linkages("Role", "What")
        
        # Remove linkage
        rule = self.manager.linkage_rules["Role"]["What"]
        rule.remove_linked_option("Write Code")
        assert not self.manager.should_restore_linkages("Role", "What")
    
    def test_clear_subsequent_selections(self):
        """Test clearing selections for subsequent combo boxes."""
        self.manager.register_combo_box("Role", 0)
        self.manager.register_combo_box("What", 1)
        self.manager.register_combo_box("Why", 2)
        
        # Set selections
        self.manager.update_selection("Role", "Programmer")
        self.manager.update_selection("What", "Write Code")
        self.manager.update_selection("Why", "Deliver")
        
        # Clear subsequent to Role
        self.manager.clear_subsequent_selections("Role")
        
        assert self.manager.combo_box_states["Role"].is_selected()
        assert not self.manager.combo_box_states["What"].is_selected()
        assert not self.manager.combo_box_states["Why"].is_selected()
    
    def test_get_restoration_chain(self):
        """Test getting the chain of relationships that need restoration."""
        self.manager.register_combo_box("Role", 0)
        self.manager.register_combo_box("What", 1)
        self.manager.register_combo_box("Why", 2)
        
        # Create linkages
        self.manager.create_linkage("Role", "What", "Write Code")
        self.manager.create_linkage("What", "Why", "Deliver")
        
        # Get restoration chain for Role
        chain = self.manager.get_restoration_chain("Role")
        assert ("Role", "What") in chain
        
        # Get restoration chain for What
        chain = self.manager.get_restoration_chain("What")
        assert ("What", "Why") in chain
    
    def test_get_linkage_data_for_js(self):
        """Test getting linkage data in JavaScript format."""
        self.manager.register_combo_box("Role", 0)
        self.manager.register_combo_box("What", 1)
        
        self.manager.create_linkage("Role", "What", "Write Code")
        self.manager.create_linkage("Role", "What", "Test Code")
        
        js_data = self.manager.get_linkage_data_for_js()
        expected = {
            "Role": {
                "What": ["Write Code", "Test Code"]
            }
        }
        assert js_data == expected
    
    def test_get_current_selections_for_js(self):
        """Test getting current selections in JavaScript format."""
        self.manager.register_combo_box("Role", 0)
        self.manager.register_combo_box("What", 1)
        
        self.manager.update_selection("Role", "Programmer")
        self.manager.update_selection("What", "Write Code")
        
        js_selections = self.manager.get_current_selections_for_js()
        expected = {
            "Role": "Programmer",
            "What": "Write Code"
        }
        assert js_selections == expected
    
    def test_validate_linkage_integrity(self):
        """Test validating linkage integrity."""
        self.manager.register_combo_box("Role", 0)
        
        # Create linkage with non-existent child
        self.manager.linkage_rules["Role"] = {"NonExistent": LinkageRule("Role", "NonExistent")}
        
        errors = self.manager.validate_linkage_integrity()
        assert len(errors) == 1
        assert "Child combo box 'NonExistent' not registered" in errors[0]


class TestLinkageManagerIntegration:
    """Integration tests for the complete linkage workflow."""
    
    def setup_method(self):
        """Set up test environment."""
        self.manager = LinkageManager()
        self.manager.register_combo_box("Role", 0)
        self.manager.register_combo_box("What", 1)
        self.manager.register_combo_box("Why", 2)
    
    def test_complete_programmer_workflow(self):
        """Test the complete Programmer -> Write Code -> Deliver workflow."""
        # Step 1: User selects Programmer
        self.manager.update_selection("Role", "Programmer")
        
        # Step 2: User adds Write Code to What combo box
        self.manager.create_linkage("Role", "What", "Write Code")
        
        # Step 3: User selects Write Code
        self.manager.update_selection("What", "Write Code")
        
        # Step 4: User adds Deliver to Why combo box
        self.manager.create_linkage("What", "Why", "Deliver")
        
        # Step 5: User selects Deliver
        self.manager.update_selection("Why", "Deliver")
        
        # Verify final state
        assert self.manager.get_current_selections_for_js() == {
            "Role": "Programmer",
            "What": "Write Code", 
            "Why": "Deliver"
        }
        
        assert self.manager.get_linkage_data_for_js() == {
            "Role": {"What": ["Write Code"]},
            "What": {"Why": ["Deliver"]}
        }
    
    def test_switching_between_parent_options(self):
        """Test switching between different parent options."""
        # Create Programmer linkages
        self.manager.create_linkage("Role", "What", "Write Code")
        
        # Create Manager linkages
        self.manager.create_linkage("Role", "What", "Review Code")
        
        # Switch to Programmer
        self.manager.update_selection("Role", "Programmer")
        self.manager.clear_subsequent_selections("Role")
        
        # Verify What combo box should be restored with Write Code
        linked_options = self.manager.get_linked_options("Role", "What")
        assert "Write Code" in linked_options
        assert "Review Code" in linked_options  # Both should be available
        
        # Switch to Manager
        self.manager.update_selection("Role", "Manager")
        self.manager.clear_subsequent_selections("Role")
        
        # Verify What combo box should be restored with Review Code
        linked_options = self.manager.get_linked_options("Role", "What")
        assert "Review Code" in linked_options
        assert "Write Code" in linked_options  # Both should still be available
