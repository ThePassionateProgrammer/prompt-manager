import os
from dotenv import load_dotenv

def load_openai_api_key(env_path=None) -> str:
    load_dotenv(dotenv_path=env_path, override=True)
    key = os.getenv('OPENAI_API_KEY')
    if not key:
        raise ValueError('OpenAI API key not found in .env or environment variable')
    return key 