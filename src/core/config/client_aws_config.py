"""
Client-specific AWS configuration management

This module handles persisting AWS profile information per client,
separate from the main YAML configuration. Each client can have
their own AWS deployment settings that persist across sessions.

Version: 1.00
Author: Cloud Stack Generator Team
"""

import json
import hashlib
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List
from datetime import datetime
from src.core.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ClientAWSConfig:
    """AWS configuration specific to a client"""
    
    client_id: str = ""
    business_name: str = ""
    domain: str = ""
    aws_profile: str = ""
    bucket_name: str = ""
    bucket_region: str = "us-east-1"
    directory: str = ""
    custom_domain: str = ""
    cloudfront_distribution_id: str = ""
    last_deployment: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        """Set timestamps if not provided"""
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClientAWSConfig':
        """Create instance from dictionary"""
        return cls(**data)
    
    def is_valid_for_deployment(self) -> bool:
        """Check if configuration is complete for deployment"""
        return bool(self.aws_profile and self.bucket_name)
    
    def generate_default_bucket_name(self) -> str:
        """Generate a default S3 bucket name based on domain"""
        if self.domain:
            # Clean domain and create bucket-safe name
            clean_domain = self.domain.replace("https://", "").replace("http://", "")
            clean_domain = clean_domain.replace("www.", "").strip("/")
            safe_name = "".join(c if c.isalnum() or c == "-" else "-" for c in clean_domain.lower())
            return f"{safe_name}-website"
        elif self.business_name:
            # Use business name as fallback
            safe_name = "".join(c if c.isalnum() or c == "-" else "-" for c in self.business_name.lower())
            return f"{safe_name}-website"
        return ""


class ClientAWSConfigManager:
    """Manages client-specific AWS configurations"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize with configuration directory
        
        Args:
            config_dir: Directory to store client AWS configs. If None, uses ~/.claude/aws_configs
        """
        if config_dir is None:
            config_dir = Path.home() / ".claude" / "aws_configs"
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Index file to map client identifiers to config files
        self.index_file = self.config_dir / "client_index.json"
        self._load_index()
    
    def _load_index(self):
        """Load the client index mapping"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    self.client_index = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.client_index = {}
        else:
            self.client_index = {}
    
    def _save_index(self):
        """Save the client index mapping"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.client_index, f, indent=2)
    
    def _generate_client_id(self, business_name: str, domain: str) -> str:
        """Generate unique client ID from business name and domain"""
        # Create stable hash from business name and domain
        content = f"{business_name.lower().strip()}|{domain.lower().strip()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _get_config_file_path(self, client_id: str) -> Path:
        """Get the file path for a client's AWS config"""
        return self.config_dir / f"{client_id}.json"
    
    def save_client_aws_config(self, config: ClientAWSConfig) -> bool:
        """
        Save client AWS configuration
        
        Args:
            config: ClientAWSConfig to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate client ID if not set
            if not config.client_id:
                config.client_id = self._generate_client_id(config.business_name, config.domain)
            
            # Update timestamp
            config.updated_at = datetime.now().isoformat()
            
            # Save config file
            config_file = self._get_config_file_path(config.client_id)
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2)
            
            # Update index
            self.client_index[config.client_id] = {
                'business_name': config.business_name,
                'domain': config.domain,
                'updated_at': config.updated_at
            }
            self._save_index()
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving client AWS config: {e}")
            return False
    
    def load_client_aws_config(self, business_name: str, domain: str) -> Optional[ClientAWSConfig]:
        """
        Load client AWS configuration by business name and domain
        
        Args:
            business_name: Client business name
            domain: Client domain
            
        Returns:
            ClientAWSConfig if found, None otherwise
        """
        try:
            client_id = self._generate_client_id(business_name, domain)
            return self.load_client_aws_config_by_id(client_id)
            
        except Exception as e:
            logger.error(f"Error loading client AWS config: {e}")
            return None
    
    def load_client_aws_config_by_id(self, client_id: str) -> Optional[ClientAWSConfig]:
        """
        Load client AWS configuration by client ID
        
        Args:
            client_id: Unique client identifier
            
        Returns:
            ClientAWSConfig if found, None otherwise
        """
        try:
            config_file = self._get_config_file_path(client_id)
            
            if not config_file.exists():
                return None
            
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return ClientAWSConfig.from_dict(data)
            
        except Exception as e:
            logger.error(f"Error loading client AWS config by ID: {e}")
            return None
    
    def list_client_configs(self) -> List[Dict[str, Any]]:
        """
        List all client AWS configurations
        
        Returns:
            List of client info dictionaries
        """
        return list(self.client_index.values())
    
    def delete_client_config(self, business_name: str, domain: str) -> bool:
        """
        Delete client AWS configuration
        
        Args:
            business_name: Client business name
            domain: Client domain
            
        Returns:
            True if successful, False otherwise
        """
        try:
            client_id = self._generate_client_id(business_name, domain)
            config_file = self._get_config_file_path(client_id)
            
            # Remove config file if exists
            if config_file.exists():
                config_file.unlink()
            
            # Remove from index
            if client_id in self.client_index:
                del self.client_index[client_id]
                self._save_index()
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting client AWS config: {e}")
            return False
    
    def create_default_config(self, business_name: str, domain: str) -> ClientAWSConfig:
        """
        Create a default AWS configuration for a client
        
        Args:
            business_name: Client business name
            domain: Client domain
            
        Returns:
            New ClientAWSConfig with defaults
        """
        client_id = self._generate_client_id(business_name, domain)
        
        config = ClientAWSConfig(
            client_id=client_id,
            business_name=business_name,
            domain=domain
        )
        
        # Set default bucket name
        config.bucket_name = config.generate_default_bucket_name()
        
        return config


# Singleton instance for global access
_client_aws_manager = None

def get_client_aws_manager() -> ClientAWSConfigManager:
    """Get the global ClientAWSConfigManager instance"""
    global _client_aws_manager
    if _client_aws_manager is None:
        _client_aws_manager = ClientAWSConfigManager()
    return _client_aws_manager