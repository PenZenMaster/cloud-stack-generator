"""
Tests for client-specific AWS configuration management

Version: 1.00
Author: Cloud Stack Generator Team
"""

import tempfile
import shutil
from pathlib import Path

from src.core.config.client_aws_config import (
    ClientAWSConfig,
    ClientAWSConfigManager,
    get_client_aws_manager
)


class TestClientAWSConfig:
    """Test ClientAWSConfig model"""
    
    def test_init_with_defaults(self):
        """Test ClientAWSConfig initialization with defaults"""
        config = ClientAWSConfig()
        
        assert config.client_id == ""
        assert config.business_name == ""
        assert config.domain == ""
        assert config.aws_profile == ""
        assert config.bucket_name == ""
        assert config.bucket_region == "us-east-1"
        assert config.directory == ""
        assert config.custom_domain == ""
        assert config.cloudfront_distribution_id == ""
        assert config.last_deployment is None
        assert config.created_at != ""
        assert config.updated_at != ""
    
    def test_init_with_values(self):
        """Test ClientAWSConfig initialization with values"""
        config = ClientAWSConfig(
            client_id="test123",
            business_name="Test Business",
            domain="https://test.com",
            aws_profile="test-profile",
            bucket_name="test-bucket",
            directory="test-dir"
        )
        
        assert config.client_id == "test123"
        assert config.business_name == "Test Business"
        assert config.domain == "https://test.com"
        assert config.aws_profile == "test-profile"
        assert config.bucket_name == "test-bucket"
        assert config.directory == "test-dir"
    
    def test_is_valid_for_deployment(self):
        """Test deployment validation"""
        # Invalid - no profile or bucket
        config = ClientAWSConfig()
        assert not config.is_valid_for_deployment()
        
        # Invalid - only profile
        config.aws_profile = "test-profile"
        assert not config.is_valid_for_deployment()
        
        # Invalid - only bucket
        config.aws_profile = ""
        config.bucket_name = "test-bucket"
        assert not config.is_valid_for_deployment()
        
        # Valid - both profile and bucket
        config.aws_profile = "test-profile"
        config.bucket_name = "test-bucket"
        assert config.is_valid_for_deployment()
    
    def test_generate_default_bucket_name(self):
        """Test default bucket name generation"""
        config = ClientAWSConfig()
        
        # Test with domain
        config.domain = "https://example.com"
        assert config.generate_default_bucket_name() == "example-com-website"
        
        # Test with www domain
        config.domain = "https://www.example.com"
        assert config.generate_default_bucket_name() == "example-com-website"
        
        # Test with business name fallback
        config.domain = ""
        config.business_name = "Test Business & Co."
        assert config.generate_default_bucket_name() == "test-business---co--website"
        
        # Test with no domain or business name
        config.business_name = ""
        assert config.generate_default_bucket_name() == ""
    
    def test_to_dict_from_dict(self):
        """Test serialization methods"""
        original = ClientAWSConfig(
            client_id="test123",
            business_name="Test Business",
            domain="https://test.com",
            aws_profile="test-profile"
        )
        
        # Convert to dict and back
        data = original.to_dict()
        restored = ClientAWSConfig.from_dict(data)
        
        assert restored.client_id == original.client_id
        assert restored.business_name == original.business_name
        assert restored.domain == original.domain
        assert restored.aws_profile == original.aws_profile


class TestClientAWSConfigManager:
    """Test ClientAWSConfigManager"""
    
    def setup_method(self):
        """Set up test with temporary directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = ClientAWSConfigManager(Path(self.temp_dir))
    
    def teardown_method(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)
    
    def test_init(self):
        """Test manager initialization"""
        assert self.manager.config_dir.exists()
        assert self.manager.index_file.exists() or not self.manager.client_index
    
    def test_generate_client_id(self):
        """Test client ID generation"""
        client_id1 = self.manager._generate_client_id("Test Business", "https://test.com")
        client_id2 = self.manager._generate_client_id("Test Business", "https://test.com")
        client_id3 = self.manager._generate_client_id("Other Business", "https://test.com")
        
        # Same input should generate same ID
        assert client_id1 == client_id2
        # Different input should generate different ID
        assert client_id1 != client_id3
        # Should be 16 characters hex
        assert len(client_id1) == 16
        assert all(c in '0123456789abcdef' for c in client_id1)
    
    def test_create_default_config(self):
        """Test default config creation"""
        config = self.manager.create_default_config("Test Business", "https://test.com")
        
        assert config.business_name == "Test Business"
        assert config.domain == "https://test.com"
        assert config.client_id != ""
        assert config.bucket_name == "test-com-website"
        assert config.created_at != ""
    
    def test_save_and_load_config(self):
        """Test saving and loading configuration"""
        # Create config
        config = ClientAWSConfig(
            business_name="Test Business",
            domain="https://test.com",
            aws_profile="test-profile",
            bucket_name="test-bucket"
        )
        
        # Save config
        success = self.manager.save_client_aws_config(config)
        assert success
        assert config.client_id != ""  # Should be auto-generated
        
        # Load config back
        loaded = self.manager.load_client_aws_config("Test Business", "https://test.com")
        assert loaded is not None
        assert loaded.business_name == config.business_name
        assert loaded.domain == config.domain
        assert loaded.aws_profile == config.aws_profile
        assert loaded.bucket_name == config.bucket_name
        assert loaded.client_id == config.client_id
    
    def test_load_nonexistent_config(self):
        """Test loading non-existent configuration"""
        loaded = self.manager.load_client_aws_config("Nonexistent", "https://nonexistent.com")
        assert loaded is None
    
    def test_list_client_configs(self):
        """Test listing client configurations"""
        # Initially empty
        configs = self.manager.list_client_configs()
        assert len(configs) == 0
        
        # Save a config
        config = ClientAWSConfig(
            business_name="Test Business",
            domain="https://test.com"
        )
        self.manager.save_client_aws_config(config)
        
        # Should now have one config
        configs = self.manager.list_client_configs()
        assert len(configs) == 1
        assert configs[0]['business_name'] == "Test Business"
        assert configs[0]['domain'] == "https://test.com"
    
    def test_delete_client_config(self):
        """Test deleting client configuration"""
        # Create and save config
        config = ClientAWSConfig(
            business_name="Test Business",
            domain="https://test.com"
        )
        self.manager.save_client_aws_config(config)
        
        # Verify it exists
        loaded = self.manager.load_client_aws_config("Test Business", "https://test.com")
        assert loaded is not None
        
        # Delete it
        success = self.manager.delete_client_config("Test Business", "https://test.com")
        assert success
        
        # Verify it's gone
        loaded = self.manager.load_client_aws_config("Test Business", "https://test.com")
        assert loaded is None
    
    def test_update_existing_config(self):
        """Test updating existing configuration"""
        # Create and save initial config
        config = ClientAWSConfig(
            business_name="Test Business",
            domain="https://test.com",
            aws_profile="profile1"
        )
        self.manager.save_client_aws_config(config)
        original_updated_at = config.updated_at
        
        # Load and modify
        loaded = self.manager.load_client_aws_config("Test Business", "https://test.com")
        loaded.aws_profile = "profile2"
        loaded.bucket_name = "new-bucket"
        
        # Save updated config
        self.manager.save_client_aws_config(loaded)
        
        # Verify changes
        reloaded = self.manager.load_client_aws_config("Test Business", "https://test.com")
        assert reloaded.aws_profile == "profile2"
        assert reloaded.bucket_name == "new-bucket"
        assert reloaded.updated_at != original_updated_at


def test_get_client_aws_manager():
    """Test singleton manager function"""
    manager1 = get_client_aws_manager()
    manager2 = get_client_aws_manager()
    
    # Should return the same instance
    assert manager1 is manager2
    assert isinstance(manager1, ClientAWSConfigManager)


class TestIntegration:
    """Integration tests"""
    
    def setup_method(self):
        """Set up test with temporary directory"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)
    
    def test_multiple_clients_same_manager(self):
        """Test managing multiple clients with same manager"""
        manager = ClientAWSConfigManager(Path(self.temp_dir))
        
        # Create configs for different clients
        client1 = ClientAWSConfig(
            business_name="Client One",
            domain="https://client1.com",
            aws_profile="profile1"
        )
        
        client2 = ClientAWSConfig(
            business_name="Client Two", 
            domain="https://client2.com",
            aws_profile="profile2"
        )
        
        # Save both
        manager.save_client_aws_config(client1)
        manager.save_client_aws_config(client2)
        
        # Load both back
        loaded1 = manager.load_client_aws_config("Client One", "https://client1.com")
        loaded2 = manager.load_client_aws_config("Client Two", "https://client2.com")
        
        assert loaded1 is not None
        assert loaded2 is not None
        assert loaded1.aws_profile == "profile1"
        assert loaded2.aws_profile == "profile2"
        
        # List should show both
        configs = manager.list_client_configs()
        assert len(configs) == 2


def test_manager_integration_with_business_context():
    """Test manager integration with realistic business context"""
    temp_dir = tempfile.mkdtemp()
    try:
        manager = ClientAWSConfigManager(Path(temp_dir))
        
        # Simulate different clients
        clients = [
            ("Acme Corp", "https://acme-corp.com"),
            ("Beta LLC", "https://beta-llc.com"),
            ("Gamma Inc", "https://gamma.io")
        ]
        
        # Create configs for each client
        saved_configs = []
        for business_name, domain in clients:
            config = manager.create_default_config(business_name, domain)
            config.aws_profile = f"profile-{business_name.lower().replace(' ', '-')}"
            config.bucket_name = f"{business_name.lower().replace(' ', '-')}-website-bucket"
            
            success = manager.save_client_aws_config(config)
            assert success
            saved_configs.append(config)
        
        # Verify each client's config is separate and persistent
        for i, (business_name, domain) in enumerate(clients):
            loaded = manager.load_client_aws_config(business_name, domain)
            assert loaded is not None
            assert loaded.business_name == business_name
            assert loaded.domain == domain
            assert loaded.aws_profile == saved_configs[i].aws_profile
            assert loaded.bucket_name == saved_configs[i].bucket_name
            # Each should have different client ID
            if i > 0:
                prev_loaded = manager.load_client_aws_config(*clients[i-1])
                assert loaded.client_id != prev_loaded.client_id
        
        # Verify list shows all clients
        all_configs = manager.list_client_configs()
        assert len(all_configs) == 3
        
        # Test updating one client doesn't affect others
        acme_config = manager.load_client_aws_config("Acme Corp", "https://acme-corp.com")
        acme_config.bucket_region = "us-west-2"
        acme_config.directory = "prod"
        manager.save_client_aws_config(acme_config)
        
        # Verify Acme was updated
        updated_acme = manager.load_client_aws_config("Acme Corp", "https://acme-corp.com")
        assert updated_acme.bucket_region == "us-west-2"
        assert updated_acme.directory == "prod"
        
        # Verify others unchanged
        beta_config = manager.load_client_aws_config("Beta LLC", "https://beta-llc.com")
        assert beta_config.bucket_region == "us-east-1"  # default
        assert beta_config.directory == ""  # default
        
    finally:
        shutil.rmtree(temp_dir)