# tests/test_storage.py

import pytest
import os
import json
from src.prompt_manager.storage import StorageManager
from src.prompt_manager.prompt import Prompt


class TestStorageManager:
    def test_save_and_load_prompts(self, tmp_path):
        """Test saving and loading prompts."""
        storage_file = tmp_path / "test_prompts.json"
        storage = StorageManager(str(storage_file))
        
        # Create test prompts
        prompts = {}
        prompt1 = Prompt("Test 1", "Hello world", "test")
        prompt1.id = "id1"
        prompts["id1"] = prompt1
        
        prompt2 = Prompt("Test 2", "Goodbye world", "test")
        prompt2.id = "id2"
        prompts["id2"] = prompt2
        
        # Save prompts
        result = storage.save_prompts(prompts)
        assert result is True
        assert storage.file_exists()
        
        # Load prompts
        loaded_prompts = storage.load_prompts()
        assert len(loaded_prompts) == 2
        assert "id1" in loaded_prompts
        assert "id2" in loaded_prompts
        
        # Verify prompt data
        loaded_prompt1 = loaded_prompts["id1"]
        assert loaded_prompt1.name == "Test 1"
        assert loaded_prompt1.text == "Hello world"
        assert loaded_prompt1.category == "test"
        assert loaded_prompt1.id == "id1"
    
    def test_load_nonexistent_file(self, tmp_path):
        """Test loading from non-existent file returns empty dict."""
        storage_file = tmp_path / "nonexistent.json"
        storage = StorageManager(str(storage_file))
        
        prompts = storage.load_prompts()
        assert prompts == {}
    
    def test_save_prompts_with_unicode(self, tmp_path):
        """Test saving prompts with unicode characters."""
        storage_file = tmp_path / "unicode_prompts.json"
        storage = StorageManager(str(storage_file))
        
        prompts = {}
        prompt = Prompt("Test", "Hello 世界", "test")
        prompt.id = "id1"
        prompts["id1"] = prompt
        
        result = storage.save_prompts(prompts)
        assert result is True
        
        loaded_prompts = storage.load_prompts()
        assert len(loaded_prompts) == 1
        assert loaded_prompts["id1"].text == "Hello 世界"
    
    def test_delete_file(self, tmp_path):
        """Test deleting storage file."""
        storage_file = tmp_path / "delete_test.json"
        storage = StorageManager(str(storage_file))
        
        # Create a file first
        prompts = {}
        prompt = Prompt("Test", "Hello", "test")
        prompt.id = "id1"
        prompts["id1"] = prompt
        storage.save_prompts(prompts)
        assert storage.file_exists()
        
        # Delete the file
        result = storage.delete_file()
        assert result is True
        assert not storage.file_exists()
    
    def test_delete_nonexistent_file(self, tmp_path):
        """Test deleting non-existent file."""
        storage_file = tmp_path / "nonexistent.json"
        storage = StorageManager(str(storage_file))
        
        result = storage.delete_file()
        assert result is True  # Should succeed even if file doesn't exist 