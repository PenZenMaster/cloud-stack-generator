"""
Module/Script Name: S3 Manager
Path: src/core/aws/s3_manager.py

Description:
S3 operations manager implementing Cloud Stack SOP patterns for bucket management,
file uploads, and static website hosting configuration.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-09-05

Last Modified Date:
2025-09-05

Comments:
* v1.00 - Initial implementation following SOP bucket naming and caching patterns
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import mimetypes
import re

import boto3
from botocore.exceptions import ClientError, NoCredentialsError, BotoCoreError


@dataclass
class UploadProgress:
    """Upload progress tracking"""
    total_files: int = 0
    uploaded_files: int = 0
    failed_files: int = 0
    current_file: str = ""
    bytes_uploaded: int = 0
    total_bytes: int = 0
    start_time: Optional[datetime] = None


@dataclass
class UploadResult:
    """Upload operation result"""
    success: bool
    message: str
    uploaded_files: List[str] = None
    failed_files: List[str] = None
    website_url: str = ""
    
    def __post_init__(self):
        if self.uploaded_files is None:
            self.uploaded_files = []
        if self.failed_files is None:
            self.failed_files = []


class S3Manager:
    """
    S3 operations manager following Cloud Stack SOP patterns.
    
    Implements bucket creation, file upload, static website hosting,
    and caching policies as defined in the SOP documentation.
    """
    
    def __init__(self, session: Optional[boto3.Session] = None):
        """
        Initialize S3 manager with optional boto3 session.
        
        Args:
            session: Pre-configured boto3 session with credentials
        """
        self.session = session or boto3.Session()
        self.s3_client = None
        self.s3_resource = None
        self._progress_callback: Optional[Callable[[UploadProgress], None]] = None
        
        # SOP file type mappings for caching
        self.cache_settings = {
            # HTML files - short cache (5 minutes)
            'html': {'Cache-Control': 'max-age=300,public', 'Content-Type': 'text/html'},
            'htm': {'Cache-Control': 'max-age=300,public', 'Content-Type': 'text/html'},
            
            # Data files - longer cache (1 day)
            'json': {'Cache-Control': 'max-age=86400,public', 'Content-Type': 'application/json'},
            'csv': {'Cache-Control': 'max-age=86400,public', 'Content-Type': 'text/csv'},
            'xlsx': {'Cache-Control': 'max-age=86400,public', 'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'},
            
            # Static assets - long cache (1 day)
            'css': {'Cache-Control': 'max-age=86400,public', 'Content-Type': 'text/css'},
            'js': {'Cache-Control': 'max-age=86400,public', 'Content-Type': 'application/javascript'},
            'png': {'Cache-Control': 'max-age=86400,public', 'Content-Type': 'image/png'},
            'jpg': {'Cache-Control': 'max-age=86400,public', 'Content-Type': 'image/jpeg'},
            'jpeg': {'Cache-Control': 'max-age=86400,public', 'Content-Type': 'image/jpeg'},
            'gif': {'Cache-Control': 'max-age=86400,public', 'Content-Type': 'image/gif'},
            'webp': {'Cache-Control': 'max-age=86400,public', 'Content-Type': 'image/webp'},
            'svg': {'Cache-Control': 'max-age=86400,public', 'Content-Type': 'image/svg+xml'},
            'ico': {'Cache-Control': 'max-age=86400,public', 'Content-Type': 'image/x-icon'},
            
            # Documents and other files
            'txt': {'Cache-Control': 'max-age=300,public', 'Content-Type': 'text/plain'},
            'xml': {'Cache-Control': 'max-age=300,public', 'Content-Type': 'application/xml'},
            'pdf': {'Cache-Control': 'max-age=86400,public', 'Content-Type': 'application/pdf'},
        }
    
    def set_session(self, session: boto3.Session):
        """Update the boto3 session and reset clients"""
        self.session = session
        self.s3_client = None
        self.s3_resource = None
    
    def set_progress_callback(self, callback: Callable[[UploadProgress], None]):
        """Set callback for upload progress updates"""
        self._progress_callback = callback
    
    def _get_s3_client(self):
        """Get or create S3 client"""
        if not self.s3_client:
            self.s3_client = self.session.client('s3')
        return self.s3_client
    
    def _get_s3_resource(self):
        """Get or create S3 resource"""
        if not self.s3_resource:
            self.s3_resource = self.session.resource('s3')
        return self.s3_resource
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test S3 connection and permissions"""
        try:
            s3 = self._get_s3_client()
            s3.list_buckets()
            return True, "S3 connection successful"
        except NoCredentialsError:
            return False, "No AWS credentials found"
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            return False, f"AWS Error ({error_code}): {str(e)}"
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"
    
    def create_bucket(
        self, 
        bucket_name: str, 
        region: str = "us-east-1"
    ) -> Tuple[bool, str]:
        """
        Create S3 bucket following SOP naming conventions.
        
        Args:
            bucket_name: Bucket name (should follow client-website-* pattern)
            region: AWS region
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            s3 = self._get_s3_client()
            
            # Validate bucket name follows SOP pattern
            if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$', bucket_name):
                return False, "Bucket name must be lowercase alphanumeric with hyphens"
            
            # Create bucket with region-specific logic (SOP section 8.1)
            if region == "us-east-1":
                # us-east-1 doesn't need LocationConstraint
                s3.create_bucket(Bucket=bucket_name)
            else:
                s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )
            
            return True, f"Bucket '{bucket_name}' created successfully in {region}"
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            if error_code == 'BucketAlreadyExists':
                return False, f"Bucket '{bucket_name}' already exists"
            elif error_code == 'BucketAlreadyOwnedByYou':
                return True, f"Bucket '{bucket_name}' already exists and is owned by you"
            else:
                return False, f"Failed to create bucket ({error_code}): {str(e)}"
        except Exception as e:
            return False, f"Failed to create bucket: {str(e)}"
    
    def configure_public_website(
        self, 
        bucket_name: str,
        index_document: str = "index.html",
        error_document: str = "404.html"
    ) -> Tuple[bool, str]:
        """
        Configure bucket for public static website hosting (SOP Mode A).
        
        Args:
            bucket_name: S3 bucket name
            index_document: Index document (default: index.html)
            error_document: Error document (default: 404.html)
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            s3 = self._get_s3_client()
            
            # Step 1: Disable Block Public Access (SOP section 8.2)
            s3.put_bucket_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': False,
                    'IgnorePublicAcls': False,
                    'BlockPublicPolicy': False,
                    'RestrictPublicBuckets': False
                }
            )
            
            # Step 2: Apply public read policy (SOP Appendix B)
            bucket_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
                }]
            }
            
            s3.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(bucket_policy)
            )
            
            # Step 3: Configure website hosting
            s3.put_bucket_website(
                Bucket=bucket_name,
                WebsiteConfiguration={
                    'IndexDocument': {'Suffix': index_document},
                    'ErrorDocument': {'Key': error_document}
                }
            )
            
            # Get bucket region for website URL
            try:
                location = s3.get_bucket_location(Bucket=bucket_name)
                region = location.get('LocationConstraint') or 'us-east-1'
            except:
                region = 'us-east-1'
            
            website_url = f"http://{bucket_name}.s3-website-{region}.amazonaws.com"
            
            return True, f"Public website configured. URL: {website_url}"
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            return False, f"Failed to configure website ({error_code}): {str(e)}"
        except Exception as e:
            return False, f"Failed to configure website: {str(e)}"
    
    def upload_directory(
        self,
        local_path: str,
        bucket_name: str,
        s3_prefix: str = "",
        exclude_patterns: List[str] = None
    ) -> UploadResult:
        """
        Upload directory to S3 with SOP-compliant caching headers.
        
        Args:
            local_path: Local directory path
            bucket_name: S3 bucket name
            s3_prefix: S3 key prefix (folder)
            exclude_patterns: File patterns to exclude
            
        Returns:
            UploadResult: Upload operation result
        """
        if exclude_patterns is None:
            exclude_patterns = ['.git', '.DS_Store', 'Thumbs.db', '*.tmp']
        
        try:
            local_path = Path(local_path)
            if not local_path.exists() or not local_path.is_dir():
                return UploadResult(False, f"Local directory '{local_path}' not found")
            
            # Collect files to upload
            files_to_upload = []
            total_bytes = 0
            
            for file_path in local_path.rglob('*'):
                if file_path.is_file():
                    # Check exclude patterns
                    if any(self._matches_pattern(file_path.name, pattern) for pattern in exclude_patterns):
                        continue
                    
                    files_to_upload.append(file_path)
                    total_bytes += file_path.stat().st_size
            
            if not files_to_upload:
                return UploadResult(False, "No files found to upload")
            
            # Initialize progress tracking
            progress = UploadProgress(
                total_files=len(files_to_upload),
                total_bytes=total_bytes,
                start_time=datetime.now()
            )
            
            s3 = self._get_s3_client()
            uploaded_files = []
            failed_files = []
            bytes_uploaded = 0
            
            for file_path in files_to_upload:
                try:
                    # Calculate S3 key
                    relative_path = file_path.relative_to(local_path)
                    s3_key = str(relative_path).replace('\\', '/')
                    if s3_prefix:
                        s3_key = f"{s3_prefix.rstrip('/')}/{s3_key}"
                    
                    # Update progress
                    progress.current_file = str(relative_path)
                    if self._progress_callback:
                        self._progress_callback(progress)
                    
                    # Get file metadata based on extension
                    file_ext = file_path.suffix.lstrip('.').lower()
                    metadata = self._get_file_metadata(file_ext)
                    
                    # Upload file
                    s3.upload_file(
                        str(file_path),
                        bucket_name,
                        s3_key,
                        ExtraArgs=metadata
                    )
                    
                    uploaded_files.append(s3_key)
                    file_size = file_path.stat().st_size
                    bytes_uploaded += file_size
                    progress.bytes_uploaded = bytes_uploaded
                    progress.uploaded_files += 1
                    
                except Exception as e:
                    print(f"Failed to upload {file_path}: {e}")
                    failed_files.append(str(relative_path))
                    progress.failed_files += 1
            
            # Final progress update
            if self._progress_callback:
                self._progress_callback(progress)
            
            success = len(uploaded_files) > 0
            message = f"Uploaded {len(uploaded_files)} files"
            if failed_files:
                message += f", {len(failed_files)} failed"
            
            return UploadResult(
                success=success,
                message=message,
                uploaded_files=uploaded_files,
                failed_files=failed_files
            )
            
        except Exception as e:
            return UploadResult(False, f"Upload failed: {str(e)}")
    
    def get_website_url(self, bucket_name: str, region: str = None) -> Optional[str]:
        """Get S3 static website URL"""
        try:
            if not region:
                s3 = self._get_s3_client()
                location = s3.get_bucket_location(Bucket=bucket_name)
                region = location.get('LocationConstraint') or 'us-east-1'
            
            return f"http://{bucket_name}.s3-website-{region}.amazonaws.com"
            
        except Exception as e:
            print(f"Error getting website URL: {e}")
            return None
    
    def list_bucket_contents(
        self, 
        bucket_name: str, 
        prefix: str = ""
    ) -> List[Dict[str, Any]]:
        """List bucket contents with metadata"""
        try:
            s3 = self._get_s3_client()
            
            response = s3.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix
            )
            
            objects = []
            for obj in response.get('Contents', []):
                objects.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'etag': obj['ETag']
                })
            
            return objects
            
        except Exception as e:
            print(f"Error listing bucket contents: {e}")
            return []
    
    def delete_bucket_contents(self, bucket_name: str, prefix: str = "") -> Tuple[bool, str]:
        """Delete all objects in bucket (or with prefix)"""
        try:
            s3 = self._get_s3_resource()
            bucket = s3.Bucket(bucket_name)
            
            objects_to_delete = []
            for obj in bucket.objects.filter(Prefix=prefix):
                objects_to_delete.append({'Key': obj.key})
            
            if not objects_to_delete:
                return True, "No objects to delete"
            
            # Delete objects in batches
            s3_client = self._get_s3_client()
            for i in range(0, len(objects_to_delete), 1000):
                batch = objects_to_delete[i:i+1000]
                s3_client.delete_objects(
                    Bucket=bucket_name,
                    Delete={'Objects': batch}
                )
            
            return True, f"Deleted {len(objects_to_delete)} objects"
            
        except Exception as e:
            return False, f"Failed to delete objects: {str(e)}"
    
    def _get_file_metadata(self, file_ext: str) -> Dict[str, str]:
        """Get S3 upload metadata for file extension"""
        if file_ext in self.cache_settings:
            return self.cache_settings[file_ext]
        
        # Default for unknown file types
        content_type, _ = mimetypes.guess_type(f"file.{file_ext}")
        return {
            'Cache-Control': 'max-age=86400,public',
            'Content-Type': content_type or 'application/octet-stream'
        }
    
    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches exclude pattern"""
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)
    
    def validate_bucket_name(self, bucket_name: str) -> Tuple[bool, str]:
        """Validate bucket name follows SOP conventions"""
        # Basic S3 bucket name rules
        if len(bucket_name) < 3 or len(bucket_name) > 63:
            return False, "Bucket name must be between 3 and 63 characters"
        
        if not re.match(r'^[a-z0-9][a-z0-9.-]*[a-z0-9]$', bucket_name):
            return False, "Bucket name must start and end with lowercase letter or number"
        
        if '..' in bucket_name:
            return False, "Bucket name cannot contain consecutive periods"
        
        # SOP-specific convention check
        if not bucket_name.startswith('client-website-'):
            return False, "Bucket name should follow SOP pattern: 'client-website-*'"
        
        return True, "Bucket name is valid"