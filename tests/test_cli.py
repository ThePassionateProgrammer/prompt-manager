# tests/test_cli.py

import pytest
import tempfile
import os
import json
from unittest.mock import patch, mock_open
from src.prompt_manager.cli import PromptManagerCLI


class TestPromptManagerCLI:
    @pytest.fixture
    def temp_cli(self):
        """Create a CLI instance with a temporary storage file."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            tmp_path = tmp.name
        
        cli = PromptManagerCLI(tmp_path)
        yield cli
        
        # Cleanup
        try:
            os.unlink(tmp_path)
        except:
            pass
    
    def test_add_prompt_with_text(self, temp_cli):
        """Test adding a prompt with provided text."""
        result = temp_cli.add_prompt("Test Prompt", "Hello world", "test")
        assert result is True
        
        # Verify prompt was added
        prompts = temp_cli.manager.list_prompts()
        assert len(prompts) == 1
        assert prompts[0].name == "Test Prompt"
        assert prompts[0].text == "Hello world"
        assert prompts[0].category == "test"
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_add_prompt_with_stdin(self, mock_print, mock_input, temp_cli):
        """Test adding a prompt by reading from stdin."""
        mock_input.side_effect = ["Line 1", "Line 2", EOFError()]
        
        result = temp_cli.add_prompt("Test Prompt", category="test")
        assert result is True
        
        # Verify prompt was added
        prompts = temp_cli.manager.list_prompts()
        assert len(prompts) == 1
        assert prompts[0].name == "Test Prompt"
        assert prompts[0].text == "Line 1\nLine 2"
        assert prompts[0].category == "test"
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_add_prompt_empty_text(self, mock_print, mock_input, temp_cli):
        """Test adding a prompt with empty text."""
        mock_input.side_effect = ["", EOFError()]
        
        result = temp_cli.add_prompt("Test Prompt")
        assert result is False
        
        # Verify no prompt was added
        prompts = temp_cli.manager.list_prompts()
        assert len(prompts) == 0
    
    def test_list_prompts_empty(self, temp_cli):
        """Test listing prompts when none exist."""
        result = temp_cli.list_prompts()
        assert result is True
    
    def test_list_prompts_with_data(self, temp_cli, capsys):
        """Test listing prompts with data."""
        # Add some prompts
        temp_cli.manager.add_prompt("Prompt 1", "Text 1", "cat1")
        temp_cli.manager.add_prompt("Prompt 2", "Text 2", "cat2")
        
        result = temp_cli.list_prompts()
        assert result is True
        
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert len(data) == 2
        assert data[0]['name'] == "Prompt 1"
        assert data[1]['name'] == "Prompt 2"
    
    def test_list_prompts_by_category(self, temp_cli, capsys):
        """Test listing prompts filtered by category."""
        # Add prompts in different categories
        temp_cli.manager.add_prompt("Prompt 1", "Text 1", "cat1")
        temp_cli.manager.add_prompt("Prompt 2", "Text 2", "cat1")
        temp_cli.manager.add_prompt("Prompt 3", "Text 3", "cat2")
        
        result = temp_cli.list_prompts("cat1")
        assert result is True
        
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert len(data) == 2
        for prompt in data:
            assert prompt['category'] == "cat1"
    
    def test_get_prompt_by_id(self, temp_cli, capsys):
        """Test getting a prompt by ID."""
        prompt_id = temp_cli.manager.add_prompt("Test Prompt", "Hello world", "test")
        
        result = temp_cli.get_prompt(prompt_id)
        assert result is True
        
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data['name'] == "Test Prompt"
        assert data['text'] == "Hello world"
        assert data['id'] == prompt_id
    
    def test_get_prompt_by_name(self, temp_cli, capsys):
        """Test getting a prompt by name."""
        temp_cli.manager.add_prompt("Test Prompt", "Hello world", "test")
        
        result = temp_cli.get_prompt("Test Prompt")
        assert result is True
        
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data['name'] == "Test Prompt"
        assert data['text'] == "Hello world"
    
    def test_get_prompt_not_found(self, temp_cli):
        """Test getting a non-existent prompt."""
        result = temp_cli.get_prompt("non-existent")
        assert result is False
    
    def test_delete_prompt_by_id(self, temp_cli):
        """Test deleting a prompt by ID."""
        prompt_id = temp_cli.manager.add_prompt("Test Prompt", "Hello world", "test")
        
        result = temp_cli.delete_prompt(prompt_id)
        assert result is True
        
        # Verify prompt was deleted
        prompts = temp_cli.manager.list_prompts()
        assert len(prompts) == 0
    
    def test_delete_prompt_by_name(self, temp_cli):
        """Test deleting a prompt by name."""
        temp_cli.manager.add_prompt("Test Prompt", "Hello world", "test")
        
        result = temp_cli.delete_prompt("Test Prompt")
        assert result is True
        
        # Verify prompt was deleted
        prompts = temp_cli.manager.list_prompts()
        assert len(prompts) == 0
    
    def test_delete_prompt_not_found(self, temp_cli):
        """Test deleting a non-existent prompt."""
        result = temp_cli.delete_prompt("non-existent")
        assert result is False
    
    def test_search_prompts_by_name(self, temp_cli, capsys):
        """Test searching prompts by name."""
        temp_cli.manager.add_prompt("Hello World", "Some text", "test")
        temp_cli.manager.add_prompt("Goodbye", "Other text", "test")
        
        result = temp_cli.search_prompts("hello")
        assert result is True
        
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert len(data) == 1
        assert data[0]['name'] == "Hello World"
    
    def test_search_prompts_by_text(self, temp_cli, capsys):
        """Test searching prompts by text content."""
        temp_cli.manager.add_prompt("Prompt 1", "Hello world text", "test")
        temp_cli.manager.add_prompt("Prompt 2", "Goodbye text", "test")
        
        result = temp_cli.search_prompts("world")
        assert result is True
        
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert len(data) == 1
        assert "world" in data[0]['text'].lower()
    
    def test_search_prompts_no_results(self, temp_cli):
        """Test searching with no results."""
        temp_cli.manager.add_prompt("Test Prompt", "Some text", "test")
        
        result = temp_cli.search_prompts("nonexistent")
        assert result is True 