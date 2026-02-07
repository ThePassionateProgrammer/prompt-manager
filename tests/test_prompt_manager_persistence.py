# tests/test_prompt_manager_persistence.py

import pytest
import os
from src.prompt_manager.prompt_manager import PromptManager


class TestPromptManagerPersistence:
    def test_prompt_manager_loads_existing_data(self, tmp_path):
        """Test that PromptManager loads existing data on initialization."""
        storage_file = tmp_path / "test_prompts.json"
        
        # Create manager and add prompts
        manager1 = PromptManager(str(storage_file))
        prompt_id1 = manager1.add_prompt("Test 1", "Hello world", "test")
        prompt_id2 = manager1.add_prompt("Test 2", "Goodbye world", "test")
        
        # Create new manager instance - should load existing data
        manager2 = PromptManager(str(storage_file))
        assert len(manager2.prompts) == 2
        
        # Verify prompts are loaded correctly
        prompt1 = manager2.get_prompt(prompt_id1)
        assert prompt1 is not None
        assert prompt1.name == "Test 1"
        assert prompt1.text == "Hello world"
        
        prompt2 = manager2.get_prompt(prompt_id2)
        assert prompt2 is not None
        assert prompt2.name == "Test 2"
        assert prompt2.text == "Goodbye world"
    
    def test_prompt_manager_saves_on_add(self, tmp_path):
        """Test that PromptManager saves data when adding prompts."""
        storage_file = tmp_path / "test_prompts.json"
        manager = PromptManager(str(storage_file))
        
        # Add a prompt
        prompt_id = manager.add_prompt("Test", "Hello world", "test")
        
        # Verify file was created
        assert os.path.exists(storage_file)
        
        # Verify data is in file
        with open(storage_file, 'r') as f:
            data = f.read()
            assert "Test" in data
            assert "Hello world" in data
    
    def test_prompt_manager_saves_on_delete(self, tmp_path):
        """Test that PromptManager saves data when deleting prompts."""
        storage_file = tmp_path / "test_prompts.json"
        manager = PromptManager(str(storage_file))
        
        # Add a prompt
        prompt_id = manager.add_prompt("Test", "Hello world", "test")
        
        # Delete the prompt
        result = manager.delete_prompt(prompt_id)
        assert result is True
        
        # Create new manager to verify deletion was saved
        manager2 = PromptManager(str(storage_file))
        assert len(manager2.prompts) == 0
    
    def test_prompt_manager_saves_on_update(self, tmp_path):
        """Test that PromptManager saves data when updating prompts."""
        storage_file = tmp_path / "test_prompts.json"
        manager = PromptManager(str(storage_file))
        
        # Add a prompt
        prompt_id = manager.add_prompt("Original", "Original text", "original")
        
        # Update the prompt
        result = manager.update_prompt(prompt_id, "Updated", "Updated text", "updated")
        assert result is True
        
        # Create new manager to verify update was saved
        manager2 = PromptManager(str(storage_file))
        prompt = manager2.get_prompt(prompt_id)
        assert prompt.name == "Updated"
        assert prompt.text == "Updated text"
        assert prompt.category == "updated"
    
    def test_prompt_manager_handles_storage_errors_gracefully(self, tmp_path):
        """Test that PromptManager handles storage errors gracefully."""
        # Try to use a directory as storage file (should cause error)
        storage_file = tmp_path / "test_dir"
        storage_file.mkdir()  # Create directory
        
        # Should not raise exception, should just fail to save
        manager = PromptManager(str(storage_file))
        prompt_id = manager.add_prompt("Test", "Hello world", "test")
        
        # The add should succeed in memory, but save might fail
        assert prompt_id in manager.prompts 