from prompt_manager.prompt import Prompt

def test_create_prompt():
    prompt = Prompt(
        name="Welcome Prompt",
        text="Hello, how can I help you today?",
        category="greeting"
    )
    
    assert prompt.name == "Welcome Prompt"
    assert prompt.text.startswith("Hello")
    assert prompt.category == "greeting"