"""
Filename: api_key_manager.py
Path: E:/projects/cloud-stack-generator/src/core/security/api_key_manager.py
Description: Secure API key storage manager
Stores API keys separately from configuration files to prevent exposure

Version: 1.0.0
Date: 2025-08-15
Author: Cloud Stack Generator Team
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, Optional
import base64


class APIKeyManager:
    """Secure API key storage manager"""
    
    def __init__(self):
        # Store keys in user's local app data, not in source control
        self.app_data_dir = Path.home() / ".cloud-stack-generator"
        self.keys_file = self.app_data_dir / "api_keys.dat"
        
        # Ensure directory exists
        self.app_data_dir.mkdir(exist_ok=True)
    
    def _encode_data(self, data: str) -> str:
        """Simple base64 encoding for basic obfuscation"""
        return base64.b64encode(data.encode()).decode()
    
    def _decode_data(self, encoded_data: str) -> str:
        """Simple base64 decoding"""
        try:
            return base64.b64decode(encoded_data.encode()).decode()
        except Exception:
            return ""
    
    def _load_keys(self) -> Dict[str, str]:
        """Load stored API keys"""
        if not self.keys_file.exists():
            return {}
        
        try:
            with open(self.keys_file, 'r', encoding='utf-8') as f:
                encoded_data = f.read().strip()
            
            if not encoded_data:
                return {}
            
            json_data = self._decode_data(encoded_data)
            return json.loads(json_data) if json_data else {}
        except Exception as e:
            print(f"Warning: Could not load API keys: {e}")
            return {}
    
    def _save_keys(self, keys: Dict[str, str]) -> bool:
        """Save API keys with basic obfuscation"""
        try:
            json_data = json.dumps(keys)
            encoded_data = self._encode_data(json_data)
            
            with open(self.keys_file, 'w', encoding='utf-8') as f:
                f.write(encoded_data)
            
            # Set restrictive permissions (owner only) on Unix-like systems
            try:
                os.chmod(self.keys_file, 0o600)
            except (OSError, AttributeError):
                # chmod may not work on Windows, that's okay
                pass
            
            return True
        except Exception as e:
            print(f"Error: Could not save API keys: {e}")
            return False
    
    def set_api_key(self, service: str, api_key: str) -> bool:
        """Store an API key securely"""
        keys = self._load_keys()
        keys[service] = api_key
        return self._save_keys(keys)
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Retrieve an API key"""
        keys = self._load_keys()
        return keys.get(service)
    
    def remove_api_key(self, service: str) -> bool:
        """Remove an API key"""
        keys = self._load_keys()
        if service in keys:
            del keys[service]
            return self._save_keys(keys)
        return True
    
    def list_services(self) -> list:
        """List services with stored API keys"""
        keys = self._load_keys()
        return list(keys.keys())
    
    def clear_all_keys(self) -> bool:
        """Clear all stored API keys"""
        return self._save_keys({})


# Global instance
api_key_manager = APIKeyManager()