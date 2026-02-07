# tests/test_prompt.py

from src.prompt_manager.prompt import Prompt
import time

def test_prompt_creation():
    prompt = Prompt("Greeting", "Hello, world!", category="intro")
    assert prompt.name == "Greeting"
    assert prompt.text == "Hello, world!"
    assert prompt.category == "intro"
    assert prompt.created_at == prompt.modified_at

def test_prompt_update_changes_text_and_timestamp():
    prompt = Prompt("Test", "Old text")
    old_time = prompt.modified_at

    time.sleep(0.01)  # Ensure timestamp changes
    prompt.update_text("New text")

    assert prompt.text == "New text"
    assert prompt.modified_at > old_time