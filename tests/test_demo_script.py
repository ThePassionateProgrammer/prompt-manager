# tests/test_demo_script.py

import pytest
import tempfile
import os
import json
from unittest.mock import patch
from demo_script import main


class TestDemoScript:
    def test_demo_script_runs_successfully(self, capsys):
        """Test that the demo script runs without errors and produces expected output."""
        with patch('demo_script.PromptManager') as mock_manager_class:
            # Mock the PromptManager
            mock_manager = mock_manager_class.return_value
            
            # Mock the add_prompt method to return fake IDs
            mock_manager.add_prompt.side_effect = ["fake-id-1", "fake-id-2"]
            
            # Mock the list_prompts method
            from src.prompt_manager.prompt import Prompt
            prompt1 = Prompt("Greeting Prompt", "Hello! How can I assist you today?", "greeting")
            prompt1.id = "fake-id-1"
            prompt2 = Prompt("Farewell Prompt", "Thank you for using our service. Have a great day!", "farewell")
            prompt2.id = "fake-id-2"
            mock_manager.list_prompts.return_value = [prompt1, prompt2]
            
            # Mock the get_prompt method
            mock_manager.get_prompt.return_value = prompt1
            
            # Run the demo script
            result = main()
            
            # Check return value
            assert result == 0
            
            # Check that methods were called correctly
            assert mock_manager.add_prompt.call_count == 2
            assert mock_manager.list_prompts.call_count == 1
            assert mock_manager.get_prompt.call_count == 1
            
            # Check captured output
            captured = capsys.readouterr()
            output = captured.out
            
            # Verify key output elements
            assert "=== Prompt Manager Demo ===" in output
            assert "Adding prompts..." in output
            assert "Added prompt 1 with ID: fake-id-1" in output
            assert "Added prompt 2 with ID: fake-id-2" in output
            assert "All prompts in storage:" in output
            assert "Retrieving first prompt" in output
            assert "Greeting Prompt" in output
            assert "Hello! How can I assist you today?" in output
            assert "=== Demo completed successfully! ===" in output
    
    def test_demo_script_with_real_manager(self, tmp_path):
        """Test the demo script with a real PromptManager using temporary storage."""
        # Create a temporary storage file
        storage_file = tmp_path / "test_demo.json"
        
        # Patch the storage file path in the demo script
        with patch('demo_script.PromptManager') as mock_manager_class:
            # Use a real PromptManager but with our temp file
            from src.prompt_manager.prompt_manager import PromptManager
            mock_manager_class.return_value = PromptManager(str(storage_file))
            
            # Run the demo script
            result = main()
            
            # Check return value
            assert result == 0
            
            # Verify the storage file was created
            assert storage_file.exists()
            
            # Verify the file contains the expected data
            with open(storage_file, 'r') as f:
                data = json.load(f)
                assert 'prompts' in data
                assert len(data['prompts']) == 2
                
                # Check that both prompts are in the file
                prompt_names = [p['name'] for p in data['prompts'].values()]
                assert "Greeting Prompt" in prompt_names
                assert "Farewell Prompt" in prompt_names 