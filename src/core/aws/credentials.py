"""
Module/Script Name: AWS Credentials Manager
Path: src/core/aws/credentials.py

Description:
AWS credential management system supporting multiple authentication methods
including SSO, AssumeRole, and Access Keys following Cloud Stack SOP security patterns.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-09-05

Last Modified Date:
2025-09-05

Comments:
* v1.00 - Initial implementation following SOP least-privilege patterns
"""

import json
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, BotoCoreError
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import subprocess
import os
from pathlib import Path


class AuthMethod(Enum):
    """Supported AWS authentication methods"""
    ACCESS_KEYS = "access_keys"
    SSO = "sso"
    ASSUME_ROLE = "assume_role"


@dataclass
class AWSProfile:
    """AWS profile configuration"""
    name: str
    auth_method: AuthMethod
    region: str = "us-east-1"
    account_id: str = ""
    role_name: str = ""
    
    # SSO specific
    sso_start_url: str = ""
    sso_region: str = ""
    
    # AssumeRole specific
    source_profile: str = ""
    role_arn: str = ""
    
    # Metadata
    description: str = ""
    last_used: Optional[str] = None
    is_active: bool = False


class AWSCredentialsManager:
    """
    AWS credential management following Cloud Stack SOP patterns.
    
    Supports SSO, AssumeRole, and Access Key authentication methods
    with secure credential storage and validation.
    """
    
    def __init__(self):
        self.profiles: Dict[str, AWSProfile] = {}
        self.active_profile: Optional[str] = None
        self._session_cache: Dict[str, boto3.Session] = {}
        
        # Profile persistence configuration
        self._profiles_dir = Path.home() / ".claude" / "aws_profiles"
        self._profiles_file = self._profiles_dir / "profiles.json"
        
        # Ensure profiles directory exists
        self._profiles_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing profiles
        self._load_profiles()
        
    def add_sso_profile(
        self, 
        name: str, 
        sso_start_url: str, 
        sso_region: str = "us-east-1",
        region: str = "us-east-1"
    ) -> AWSProfile:
        """Add SSO profile following SOP Identity Center patterns"""
        profile = AWSProfile(
            name=name,
            auth_method=AuthMethod.SSO,
            region=region,
            sso_start_url=sso_start_url,
            sso_region=sso_region,
            description=f"SSO profile for {name}"
        )
        
        self.profiles[name] = profile
        self._save_profiles()  # Persist the new profile
        return profile
    
    def add_assume_role_profile(
        self,
        name: str,
        source_profile: str,
        role_arn: str,
        region: str = "us-east-1"
    ) -> AWSProfile:
        """Add AssumeRole profile for cross-account access"""
        profile = AWSProfile(
            name=name,
            auth_method=AuthMethod.ASSUME_ROLE,
            region=region,
            source_profile=source_profile,
            role_arn=role_arn,
            description=f"AssumeRole profile for {name}"
        )
        
        self.profiles[name] = profile
        self._save_profiles()  # Persist the new profile
        return profile
    
    def add_access_key_profile(
        self,
        name: str,
        region: str = "us-east-1"
    ) -> AWSProfile:
        """Add Access Key profile (keys stored securely via api_key_manager)"""
        profile = AWSProfile(
            name=name,
            auth_method=AuthMethod.ACCESS_KEYS,
            region=region,
            description=f"Access Key profile for {name}"
        )
        
        self.profiles[name] = profile
        self._save_profiles()  # Persist the new profile
        return profile
    
    def validate_profile(self, profile_name: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate AWS profile and return connection details.
        
        Returns:
            Tuple[bool, str, Dict]: (is_valid, message, identity_info)
        """
        if profile_name not in self.profiles:
            return False, f"Profile '{profile_name}' not found", {}
        
        profile = self.profiles[profile_name]
        
        try:
            session = self._get_session(profile_name)
            sts = session.client('sts')
            
            # Get caller identity to validate credentials
            identity = sts.get_caller_identity()
            
            # Extract account ID for profile
            account_id = identity['Account']
            profile.account_id = account_id
            
            identity_info = {
                'account': account_id,
                'user_id': identity['UserId'],
                'arn': identity['Arn'],
                'region': profile.region
            }
            
            return True, f"Profile '{profile_name}' validated successfully", identity_info
            
        except NoCredentialsError:
            return False, f"No credentials configured for profile '{profile_name}'", {}
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            return False, f"AWS Error ({error_code}): {str(e)}", {}
        except Exception as e:
            return False, f"Validation failed: {str(e)}", {}
    
    def test_s3_permissions(self, profile_name: str) -> Tuple[bool, str]:
        """Test S3 permissions following SOP least-privilege patterns"""
        try:
            session = self._get_session(profile_name)
            s3 = session.client('s3')
            
            # Test basic S3 list operation
            s3.list_buckets()
            
            return True, "S3 permissions validated successfully"
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'AccessDenied')
            return False, f"S3 permission test failed ({error_code}): {str(e)}"
        except Exception as e:
            return False, f"S3 permission test failed: {str(e)}"
    
    def list_client_buckets(self, profile_name: str, prefix: str = "client-website-") -> List[Dict[str, Any]]:
        """List buckets following SOP naming conventions"""
        try:
            session = self._get_session(profile_name)
            s3 = session.client('s3')
            
            response = s3.list_buckets()
            buckets = []
            
            for bucket in response.get('Buckets', []):
                bucket_name = bucket['Name']
                if bucket_name.startswith(prefix):
                    # Get bucket region
                    try:
                        location = s3.get_bucket_location(Bucket=bucket_name)
                        region = location.get('LocationConstraint') or 'us-east-1'
                    except:
                        region = 'unknown'
                    
                    buckets.append({
                        'name': bucket_name,
                        'creation_date': bucket['CreationDate'],
                        'region': region
                    })
            
            return buckets
            
        except Exception as e:
            print(f"Error listing buckets: {e}")
            return []
    
    def set_active_profile(self, profile_name: str) -> bool:
        """Set active profile for deployment operations"""
        if profile_name not in self.profiles:
            return False
        
        # Validate profile before activating
        is_valid, message, _ = self.validate_profile(profile_name)
        if not is_valid:
            print(f"Cannot activate profile: {message}")
            return False
        
        # Deactivate current profile
        if self.active_profile:
            self.profiles[self.active_profile].is_active = False
        
        # Activate new profile
        self.active_profile = profile_name
        self.profiles[profile_name].is_active = True
        
        return True
    
    def get_active_session(self) -> Optional[boto3.Session]:
        """Get boto3 session for active profile"""
        if not self.active_profile:
            return None
        
        return self._get_session(self.active_profile)
    
    def _get_session(self, profile_name: str) -> boto3.Session:
        """Get or create boto3 session for profile"""
        if profile_name in self._session_cache:
            return self._session_cache[profile_name]
        
        profile = self.profiles[profile_name]
        
        if profile.auth_method == AuthMethod.SSO:
            session = self._create_sso_session(profile)
        elif profile.auth_method == AuthMethod.ASSUME_ROLE:
            session = self._create_assume_role_session(profile)
        elif profile.auth_method == AuthMethod.ACCESS_KEYS:
            session = self._create_access_key_session(profile)
        else:
            raise ValueError(f"Unsupported auth method: {profile.auth_method}")
        
        self._session_cache[profile_name] = session
        return session
    
    def _create_sso_session(self, profile: AWSProfile) -> boto3.Session:
        """Create SSO session using AWS CLI profile"""
        # For SSO, we rely on AWS CLI profile configuration
        # User must run `aws configure sso --profile {profile.name}` first
        session = boto3.Session(profile_name=profile.name, region_name=profile.region)
        return session
    
    def _create_assume_role_session(self, profile: AWSProfile) -> boto3.Session:
        """Create AssumeRole session"""
        # Get source session
        if profile.source_profile not in self.profiles:
            raise ValueError(f"Source profile '{profile.source_profile}' not found")
        
        source_session = self._get_session(profile.source_profile)
        sts = source_session.client('sts')
        
        # Assume role
        response = sts.assume_role(
            RoleArn=profile.role_arn,
            RoleSessionName=f"{profile.name}-session"
        )
        
        credentials = response['Credentials']
        
        session = boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'],
            region_name=profile.region
        )
        
        return session
    
    def _create_access_key_session(self, profile: AWSProfile) -> boto3.Session:
        """Create session with stored access keys"""
        # Access keys would be retrieved from secure storage
        # For now, fall back to default credential chain
        session = boto3.Session(region_name=profile.region)
        return session
    
    def export_profiles(self) -> Dict[str, Any]:
        """Export profiles configuration (without sensitive data)"""
        export_data = {
            'profiles': {},
            'active_profile': self.active_profile
        }
        
        for name, profile in self.profiles.items():
            export_data['profiles'][name] = {
                'name': profile.name,
                'auth_method': profile.auth_method.value,
                'region': profile.region,
                'account_id': profile.account_id,
                'description': profile.description,
                'last_used': profile.last_used,
                'is_active': profile.is_active,
                # Include non-sensitive config
                'sso_start_url': profile.sso_start_url,
                'sso_region': profile.sso_region,
                'role_arn': profile.role_arn,
                'source_profile': profile.source_profile
            }
        
        return export_data
    
    def import_profiles(self, data: Dict[str, Any]) -> bool:
        """Import profiles configuration"""
        try:
            for name, profile_data in data.get('profiles', {}).items():
                auth_method = AuthMethod(profile_data['auth_method'])
                
                profile = AWSProfile(
                    name=profile_data['name'],
                    auth_method=auth_method,
                    region=profile_data['region'],
                    account_id=profile_data.get('account_id', ''),
                    description=profile_data.get('description', ''),
                    sso_start_url=profile_data.get('sso_start_url', ''),
                    sso_region=profile_data.get('sso_region', ''),
                    role_arn=profile_data.get('role_arn', ''),
                    source_profile=profile_data.get('source_profile', ''),
                    last_used=profile_data.get('last_used'),
                    is_active=profile_data.get('is_active', False)
                )
                
                self.profiles[name] = profile
            
            self.active_profile = data.get('active_profile')
            return True
            
        except Exception as e:
            print(f"Error importing profiles: {e}")
            return False
    
    def _load_profiles(self) -> None:
        """Load profiles from persistent storage"""
        try:
            if self._profiles_file.exists():
                with open(self._profiles_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.import_profiles(data)
        except Exception as e:
            print(f"Warning: Could not load AWS profiles: {e}")
            # Continue with empty profiles if loading fails
    
    def _save_profiles(self) -> None:
        """Save profiles to persistent storage"""
        try:
            data = self.export_profiles()
            with open(self._profiles_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save AWS profiles: {e}")


# Utility functions for AWS CLI integration
def check_aws_cli() -> Tuple[bool, str]:
    """Check if AWS CLI is installed and accessible"""
    try:
        result = subprocess.run(['aws', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, "AWS CLI not accessible"
    except subprocess.TimeoutExpired:
        return False, "AWS CLI command timed out"
    except FileNotFoundError:
        return False, "AWS CLI not found - please install AWS CLI v2"
    except Exception as e:
        return False, f"AWS CLI check failed: {str(e)}"


def get_aws_config_profiles() -> List[str]:
    """Get list of configured AWS CLI profiles"""
    try:
        config_path = Path.home() / '.aws' / 'config'
        if not config_path.exists():
            return []
        
        profiles = []
        with open(config_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('[profile '):
                    profile_name = line[9:-1]  # Remove '[profile ' and ']'
                    profiles.append(profile_name)
                elif line.startswith('[') and line != '[default]':
                    # Handle [default] profile case
                    if line == '[default]':
                        profiles.append('default')
        
        return profiles
    except Exception as e:
        print(f"Error reading AWS config: {e}")
        return []