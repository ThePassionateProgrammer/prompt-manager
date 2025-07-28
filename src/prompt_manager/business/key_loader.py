import os
from dotenv import load_dotenv, set_key

def load_openai_api_key(env_path=None) -> str:
    load_dotenv(dotenv_path=env_path, override=True)
    key = os.getenv('OPENAI_API_KEY')
    if not key:
        raise ValueError('OpenAI API key not found in .env or environment variable')
    return key

def save_openai_api_key(api_key: str, env_path: str):
    """Save OpenAI API key to .env file."""
    set_key(dotenv_path=env_path, key_to_set='OPENAI_API_KEY', value_to_set=api_key) 