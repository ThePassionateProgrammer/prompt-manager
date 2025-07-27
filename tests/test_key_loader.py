import os
import tempfile
import shutil
import pytest
import importlib

# from src.prompt_manager.business.key_loader import load_openai_api_key

def test_load_key_from_env_file(monkeypatch):
    """Test loading key from a .env file."""
    temp_dir = tempfile.mkdtemp()
    env_path = os.path.join(temp_dir, '.env')
    with open(env_path, 'w') as f:
        f.write('OPENAI_API_KEY=sk-test123\n')
    monkeypatch.chdir(temp_dir)
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    import src.prompt_manager.business.key_loader as key_loader
    importlib.reload(key_loader)
    key = key_loader.load_openai_api_key(env_path)
    assert key == 'sk-test123'
    shutil.rmtree(temp_dir)

def test_load_key_from_env_var(monkeypatch):
    """Test loading key from environment variable if .env is missing."""
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-env456')
    from src.prompt_manager.business.key_loader import load_openai_api_key
    key = load_openai_api_key()
    assert key == 'sk-env456'

def test_load_key_missing(monkeypatch):
    """Test error when key is missing from both .env and environment."""
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    from src.prompt_manager.business.key_loader import load_openai_api_key
    with pytest.raises(ValueError):
        load_openai_api_key() 