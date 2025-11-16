"""
Tests for S3 bucket name validation with SOP patterns

Version: 1.00
Author: Cloud Stack Generator Team
"""

import pytest
from src.core.aws.s3_manager import S3Manager


class TestS3BucketValidation:
    """Test S3 bucket name validation"""
    
    def setup_method(self):
        """Setup S3Manager for testing"""
        self.s3_manager = S3Manager()
    
    def test_salvo_profile_bucket_name(self):
        """Test that salvo-metal-works-fabrication is valid for Salvo-Cloud profile"""
        bucket_name = "salvo-metal-works-fabrication"
        is_valid, message = self.s3_manager.validate_bucket_name(bucket_name)
        
        assert is_valid == True
        assert message == "Bucket name is valid"
    
    def test_client_website_pattern(self):
        """Test original client-website SOP pattern"""
        valid_names = [
            "client-website-test123",
            "client-website-prod",
            "client-website-staging-2024"
        ]
        
        for name in valid_names:
            is_valid, message = self.s3_manager.validate_bucket_name(name)
            assert is_valid == True, f"Expected {name} to be valid: {message}"
    
    def test_business_website_pattern(self):
        """Test business-website SOP pattern"""
        valid_names = [
            "acme-website",
            "salvo-website",
            "business123-website",
            "my-company-website"
        ]
        
        for name in valid_names:
            is_valid, message = self.s3_manager.validate_bucket_name(name)
            assert is_valid == True, f"Expected {name} to be valid: {message}"
    
    def test_business_specific_pattern(self):
        """Test business-specific naming pattern"""
        valid_names = [
            "salvo-metal-works-fabrication",
            "acme-corp-production",
            "johnson-plumbing-services",
            "tech-solutions-dev",
            "my-business-name",
            "valid.bucket.name"  # Periods are allowed in S3 bucket names
        ]
        
        for name in valid_names:
            is_valid, message = self.s3_manager.validate_bucket_name(name)
            assert is_valid == True, f"Expected {name} to be valid: {message}"
    
    def test_invalid_bucket_names(self):
        """Test invalid bucket names"""
        invalid_names = [
            "UPPERCASE-BUCKET",     # Contains uppercase
            "ab",                   # Too short
            "bucket_with_underscore", # Contains underscore
            "-starts-with-hyphen",  # Starts with hyphen
            "ends-with-hyphen-",    # Ends with hyphen
            "has..consecutive.periods", # Consecutive periods
        ]
        
        for name in invalid_names:
            is_valid, message = self.s3_manager.validate_bucket_name(name)
            assert is_valid == False, f"Expected {name} to be invalid but got: {message}"
    
    def test_edge_cases(self):
        """Test edge cases for bucket naming"""
        # Minimum length (3 characters) with valid pattern
        is_valid, _ = self.s3_manager.validate_bucket_name("a-b")
        assert is_valid == True
        
        # Just under minimum
        is_valid, _ = self.s3_manager.validate_bucket_name("ab")
        assert is_valid == False
        
        # Maximum length (63 characters) - valid pattern
        max_length_name = "a" * 60 + "-bc"  # 63 chars total, follows business pattern
        is_valid, _ = self.s3_manager.validate_bucket_name(max_length_name)
        assert is_valid == True
        
        # Over maximum length
        over_max_name = "a" * 64
        is_valid, _ = self.s3_manager.validate_bucket_name(over_max_name)
        assert is_valid == False
    
    def test_real_world_client_names(self):
        """Test realistic client bucket names"""
        client_buckets = [
            "salvo-metal-works-fabrication",    # Salvo-Cloud profile
            "acme-corp-website-prod",           # Corporate site
            "johnson-plumbing-website",         # Service business
            "tech-solutions-staging",           # Staging environment
            "client-website-demo-2024",         # Standard SOP pattern
            "my-restaurant-website",            # Restaurant business
            "consulting-firm-assets"            # Business assets
        ]
        
        for bucket_name in client_buckets:
            is_valid, message = self.s3_manager.validate_bucket_name(bucket_name)
            assert is_valid == True, f"Real-world name '{bucket_name}' should be valid: {message}"
    
    def test_sop_pattern_flexibility(self):
        """Test that SOP patterns are flexible for different business types"""
        business_types = [
            "manufacturing-company-site",
            "retail-store-website", 
            "service-provider-assets",
            "consulting-firm-prod",
            "restaurant-chain-staging",
            "tech-startup-website"
        ]
        
        for name in business_types:
            is_valid, message = self.s3_manager.validate_bucket_name(name)
            assert is_valid == True, f"Business type '{name}' should follow flexible SOP: {message}"