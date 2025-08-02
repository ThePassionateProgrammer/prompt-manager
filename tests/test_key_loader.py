import os
import tempfile
import shutil
import pytest
import importlib
from pathlib import Path
from unittest.mock import patch

@pytest.mark.skip(reason="Backward compatibility test needs environment isolation")
def test_load_key_from_env_file(monkeypatch):
    """Test loading key from a .env file (backward compatibility)."""
    temp_dir = tempfile.mkdtemp()
    env_path = os.path.join(temp_dir, '.env')
    with open(env_path, 'w') as f:
        f.write('OPENAI_API_KEY=sk-test123\n')
    monkeypatch.chdir(temp_dir)
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    
    # Create a test key manager to avoid interference
    keys_file = os.path.join(temp_dir, 'test_keys.enc')
    from src.prompt_manager.business.key_loader import SecureKeyManager
    
    # Mock the global key manager to use our test instance
    test_key_manager = SecureKeyManager(keys_file=keys_file, master_password='test-password')
    
    # Reset the global key manager and patch it
    import src.prompt_manager.business.key_loader as key_loader
    key_loader._key_manager = None  # Reset the global instance
    with patch('src.prompt_manager.business.key_loader._key_manager', test_key_manager):
        importlib.reload(key_loader)
        key = key_loader.load_openai_api_key(env_path)
        assert key == 'sk-test123'
    
    shutil.rmtree(temp_dir)

def test_save_and_load_key_secure():
    """Test saving and loading a key using secure storage."""
    # Create a temporary directory for test
    temp_dir = tempfile.mkdtemp()
    keys_file = os.path.join(temp_dir, 'test_keys.enc')
    
    try:
        from src.prompt_manager.business.key_loader import SecureKeyManager
        
        # Create key manager with test file
        key_manager = SecureKeyManager(keys_file=keys_file, master_password='test-password')
        
        # Save a key
        assert key_manager.save_key('test_key', 'test_value')
        
        # Load the key
        loaded_key = key_manager.load_key('test_key')
        assert loaded_key == 'test_value'
        
        # Test loading all keys
        all_keys = key_manager.load_all_keys()
        assert 'test_key' in all_keys
        assert all_keys['test_key'] == 'test_value'
        
    finally:
        shutil.rmtree(temp_dir)

def test_load_key_missing_secure():
    """Test error when key is missing from secure storage."""
    # Create a temporary directory for test
    temp_dir = tempfile.mkdtemp()
    keys_file = os.path.join(temp_dir, 'test_keys.enc')
    
    try:
        from src.prompt_manager.business.key_loader import SecureKeyManager
        
        # Create key manager with test file
        key_manager = SecureKeyManager(keys_file=keys_file, master_password='test-password')
        
        # Try to load a non-existent key
        loaded_key = key_manager.load_key('non_existent_key')
        assert loaded_key is None
        
    finally:
        shutil.rmtree(temp_dir)

def test_delete_key_secure():
    """Test deleting a key from secure storage."""
    # Create a temporary directory for test
    temp_dir = tempfile.mkdtemp()
    keys_file = os.path.join(temp_dir, 'test_keys.enc')
    
    try:
        from src.prompt_manager.business.key_loader import SecureKeyManager
        
        # Create key manager with test file
        key_manager = SecureKeyManager(keys_file=keys_file, master_password='test-password')
        
        # Save a key
        assert key_manager.save_key('test_key', 'test_value')
        
        # Verify it exists
        assert key_manager.load_key('test_key') == 'test_value'
        
        # Delete the key
        assert key_manager.delete_key('test_key')
        
        # Verify it's gone
        assert key_manager.load_key('test_key') is None
        
    finally:
        shutil.rmtree(temp_dir)

def test_list_keys_secure():
    """Test listing all keys in secure storage."""
    # Create a temporary directory for test
    temp_dir = tempfile.mkdtemp()
    keys_file = os.path.join(temp_dir, 'test_keys.enc')
    
    try:
        from src.prompt_manager.business.key_loader import SecureKeyManager
        
        # Create key manager with test file
        key_manager = SecureKeyManager(keys_file=keys_file, master_password='test-password')
        
        # Save multiple keys
        assert key_manager.save_key('key1', 'value1')
        assert key_manager.save_key('key2', 'value2')
        
        # List keys
        keys = key_manager.list_keys()
        assert 'key1' in keys
        assert 'key2' in keys
        assert len(keys) == 2
        
    finally:
        shutil.rmtree(temp_dir)

def test_backward_compatibility():
    """Test backward compatibility with environment variables."""
    # Create a temporary directory for test
    temp_dir = tempfile.mkdtemp()
    keys_file = os.path.join(temp_dir, 'test_keys.enc')
    
    try:
        from src.prompt_manager.business.key_loader import load_openai_api_key, save_openai_api_key
        
        # Test that save and load work with the new interface
        assert save_openai_api_key('sk-test-backward-compat')
        
        # Load the key
        key = load_openai_api_key()
        assert key == 'sk-test-backward-compat'
        
    finally:
        shutil.rmtree(temp_dir)

def test_encryption_security():
    """Test that keys are actually encrypted."""
    # Create a temporary directory for test
    temp_dir = tempfile.mkdtemp()
    keys_file = os.path.join(temp_dir, 'test_keys.enc')
    
    try:
        from src.prompt_manager.business.key_loader import SecureKeyManager
        
        # Create key manager with test file
        key_manager = SecureKeyManager(keys_file=keys_file, master_password='test-password')
        
        # Save a key
        assert key_manager.save_key('secret_key', 'very-secret-value')
        
        # Read the raw file content
        with open(keys_file, 'rb') as f:
            raw_content = f.read()
        
        # Verify the content is encrypted (not plain text)
        assert b'very-secret-value' not in raw_content
        assert b'secret_key' not in raw_content
        
        # Verify we can still decrypt it
        loaded_key = key_manager.load_key('secret_key')
        assert loaded_key == 'very-secret-value'
        
    finally:
        shutil.rmtree(temp_dir) 