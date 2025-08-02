import os
import json
import base64
import tempfile
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional, Dict, Any


class SecureKeyManager:
    """Secure key management system with encryption."""
    
    def __init__(self, keys_file: Optional[str] = None, master_password: Optional[str] = None):
        """Initialize the secure key manager.
        
        Args:
            keys_file: Path to the encrypted keys file. Defaults to ~/.prompt_manager/keys.enc
            master_password: Master password for encryption. If None, uses environment variable.
        """
        if keys_file is None:
            keys_file = os.path.expanduser("~/.prompt_manager/keys.enc")
        
        self.keys_file = Path(keys_file)
        self.keys_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Get master password from environment or use default for development
        self.master_password = master_password or os.getenv('PROMPT_MANAGER_MASTER_PASSWORD', 'dev-password')
        
        # Generate encryption key from master password
        self.fernet = self._create_fernet()
    
    def _create_fernet(self) -> Fernet:
        """Create Fernet cipher from master password."""
        # Use a salt for key derivation
        salt = b'prompt_manager_salt'  # In production, use a random salt per file
        
        # Derive key from master password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_password.encode()))
        return Fernet(key)
    
    def _encrypt_data(self, data: Dict[str, Any]) -> bytes:
        """Encrypt data dictionary."""
        json_data = json.dumps(data)
        return self.fernet.encrypt(json_data.encode())
    
    def _decrypt_data(self, encrypted_data: bytes) -> Dict[str, Any]:
        """Decrypt data dictionary."""
        decrypted = self.fernet.decrypt(encrypted_data)
        return json.loads(decrypted.decode())
    
    def save_key(self, key_name: str, key_value: str) -> bool:
        """Save a key securely.
        
        Args:
            key_name: Name of the key (e.g., 'openai_api_key')
            key_value: The key value to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load existing keys
            keys = self.load_all_keys()
            
            # Add/update the key
            keys[key_name] = key_value
            
            # Encrypt and save
            encrypted_data = self._encrypt_data(keys)
            self.keys_file.write_bytes(encrypted_data)
            
            return True
        except Exception as e:
            print(f"Error saving key {key_name}: {e}")
            return False
    
    def load_key(self, key_name: str) -> Optional[str]:
        """Load a specific key.
        
        Args:
            key_name: Name of the key to load
            
        Returns:
            The key value if found, None otherwise
        """
        try:
            keys = self.load_all_keys()
            return keys.get(key_name)
        except Exception as e:
            print(f"Error loading key {key_name}: {e}")
            return None
    
    def load_all_keys(self) -> Dict[str, str]:
        """Load all stored keys.
        
        Returns:
            Dictionary of all stored keys
        """
        try:
            if not self.keys_file.exists():
                return {}
            
            encrypted_data = self.keys_file.read_bytes()
            return self._decrypt_data(encrypted_data)
        except Exception as e:
            print(f"Error loading keys: {e}")
            return {}
    
    def delete_key(self, key_name: str) -> bool:
        """Delete a specific key.
        
        Args:
            key_name: Name of the key to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            keys = self.load_all_keys()
            if key_name in keys:
                del keys[key_name]
                encrypted_data = self._encrypt_data(keys)
                self.keys_file.write_bytes(encrypted_data)
                return True
            return False
        except Exception as e:
            print(f"Error deleting key {key_name}: {e}")
            return False
    
    def list_keys(self) -> list:
        """List all stored key names.
        
        Returns:
            List of key names
        """
        return list(self.load_all_keys().keys())


# Global key manager instance
_key_manager = None

def get_key_manager() -> SecureKeyManager:
    """Get the global key manager instance."""
    global _key_manager
    if _key_manager is None:
        _key_manager = SecureKeyManager()
    return _key_manager

def load_openai_api_key(env_path=None) -> str:
    """Load OpenAI API key from secure storage.
    
    This function maintains backward compatibility with the old interface.
    """
    # First try secure storage
    key_manager = get_key_manager()
    key = key_manager.load_key('openai_api_key')
    
    if key:
        return key
    
    # Fallback to .env file for backward compatibility
    if env_path and os.path.exists(env_path):
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_path, override=True)
        key = os.getenv('OPENAI_API_KEY')
        if key:
            # Store it securely for next time
            key_manager.save_key('openai_api_key', key)
            return key
    
    # Fallback to environment variable for backward compatibility
    key = os.getenv('OPENAI_API_KEY')
    if key:
        # Store it securely for next time
        key_manager.save_key('openai_api_key', key)
        return key
    
    raise ValueError('OpenAI API key not found in secure storage or environment variable')

def save_openai_api_key(api_key: str, env_path: str = None):
    """Save OpenAI API key to secure storage.
    
    This function maintains backward compatibility with the old interface.
    """
    key_manager = get_key_manager()
    return key_manager.save_key('openai_api_key', api_key)

# Additional convenience functions
def save_key(key_name: str, key_value: str) -> bool:
    """Save any key to secure storage."""
    key_manager = get_key_manager()
    return key_manager.save_key(key_name, key_value)

def load_key(key_name: str) -> Optional[str]:
    """Load any key from secure storage."""
    key_manager = get_key_manager()
    return key_manager.load_key(key_name)

def delete_key(key_name: str) -> bool:
    """Delete any key from secure storage."""
    key_manager = get_key_manager()
    return key_manager.delete_key(key_name)

def list_keys() -> list:
    """List all stored keys."""
    key_manager = get_key_manager()
    return key_manager.list_keys() 