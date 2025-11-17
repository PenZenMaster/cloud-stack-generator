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

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import mimetypes
import re

import boto3
from botocore.exceptions import ClientError, NoCredentialsError


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
    invalidation_id: str = ""
    invalidation_status: str = ""

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
            'html': {'CacheControl': 'max-age=300,public', 'ContentType': 'text/html'},
            'htm': {'CacheControl': 'max-age=300,public', 'ContentType': 'text/html'},
            
            # Data files - longer cache (1 day)
            'json': {'CacheControl': 'max-age=86400,public', 'ContentType': 'application/json'},
            'csv': {'CacheControl': 'max-age=86400,public', 'ContentType': 'text/csv'},
            'xlsx': {'CacheControl': 'max-age=86400,public', 'ContentType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'},
            
            # Static assets - long cache (1 day)
            'css': {'CacheControl': 'max-age=86400,public', 'ContentType': 'text/css'},
            'js': {'CacheControl': 'max-age=86400,public', 'ContentType': 'application/javascript'},
            'png': {'CacheControl': 'max-age=86400,public', 'ContentType': 'image/png'},
            'jpg': {'CacheControl': 'max-age=86400,public', 'ContentType': 'image/jpeg'},
            'jpeg': {'CacheControl': 'max-age=86400,public', 'ContentType': 'image/jpeg'},
            'gif': {'CacheControl': 'max-age=86400,public', 'ContentType': 'image/gif'},
            'webp': {'CacheControl': 'max-age=86400,public', 'ContentType': 'image/webp'},
            'svg': {'CacheControl': 'max-age=86400,public', 'ContentType': 'image/svg+xml'},
            'ico': {'CacheControl': 'max-age=86400,public', 'ContentType': 'image/x-icon'},
            
            # Documents and other files
            'txt': {'CacheControl': 'max-age=300,public', 'ContentType': 'text/plain'},
            'xml': {'CacheControl': 'max-age=300,public', 'ContentType': 'application/xml'},
            'pdf': {'CacheControl': 'max-age=86400,public', 'ContentType': 'application/pdf'},
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
            # Create region-specific S3 client to ensure bucket is created in correct region
            s3 = self.session.client('s3', region_name=region)
            
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
        error_document: str = "404.html",
        enable_https: bool = True
    ) -> Tuple[bool, str]:
        """
        Configure bucket for public static website hosting with HTTPS support (SOP Mode A).
        
        Args:
            bucket_name: S3 bucket name
            index_document: Index document (default: index.html)
            error_document: Error document (default: 404.html)
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # First get the bucket's actual region to use correct client
            s3_default = self._get_s3_client()
            location = s3_default.get_bucket_location(Bucket=bucket_name)
            bucket_region = location.get('LocationConstraint') or 'us-east-1'
            
            # Create region-specific client for the bucket's region
            s3 = self.session.client('s3', region_name=bucket_region)
            
            # Step 1: Disable Block Public Access (SOP section 8.2)
            s3.put_public_access_block(
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
            
            # Use the bucket region we already detected
            region = bucket_region
            
            # Generate website URL - prefer HTTPS via CloudFront if enabled
            if enable_https:
                try:
                    # Step 4: Create CloudFront distribution for HTTPS support
                    cloudfront = self.session.client('cloudfront')
                    
                    # S3 website endpoint as origin
                    if region == 'us-east-1':
                        origin_domain = f"{bucket_name}.s3-website-{region}.amazonaws.com"
                    else:
                        origin_domain = f"{bucket_name}.s3-website.{region}.amazonaws.com"
                    
                    distribution_config = {
                        'CallerReference': f"{bucket_name}-{int(datetime.now().timestamp())}",
                        'Comment': f'HTTPS distribution for {bucket_name}',
                        'DefaultRootObject': index_document,
                        'Origins': {
                            'Quantity': 1,
                            'Items': [{
                                'Id': f'{bucket_name}-origin',
                                'DomainName': origin_domain,
                                'CustomOriginConfig': {
                                    'HTTPPort': 80,
                                    'HTTPSPort': 443,
                                    'OriginProtocolPolicy': 'http-only'  # S3 website endpoint only supports HTTP
                                }
                            }]
                        },
                        'DefaultCacheBehavior': {
                            'TargetOriginId': f'{bucket_name}-origin',
                            'ViewerProtocolPolicy': 'redirect-to-https',  # Force HTTPS
                            'TrustedSigners': {
                                'Enabled': False,
                                'Quantity': 0
                            },
                            'ForwardedValues': {
                                'QueryString': False,
                                'Cookies': {
                                    'Forward': 'none'
                                }
                            },
                            'MinTTL': 0,
                            'DefaultTTL': 86400,
                            'MaxTTL': 31536000
                        },
                        'Enabled': True,
                        'PriceClass': 'PriceClass_100'  # Use only North America and Europe for cost optimization
                    }
                    
                    response = cloudfront.create_distribution(DistributionConfig=distribution_config)
                    distribution_domain = response['Distribution']['DomainName']
                    website_url = f"https://{distribution_domain}"
                    
                    return True, f"HTTPS website configured via CloudFront. URL: {website_url} (may take 10-15 minutes to deploy)"
                    
                except Exception as cf_error:
                    # Fallback to HTTP if CloudFront fails
                    print(f"CloudFront setup failed, falling back to HTTP: {cf_error}")
                    if region == 'us-east-1':
                        website_url = f"http://{bucket_name}.s3-website-{region}.amazonaws.com"
                    else:
                        website_url = f"http://{bucket_name}.s3-website.{region}.amazonaws.com"
                    
                    return True, f"Website configured with HTTP (HTTPS setup failed). URL: {website_url}"
            else:
                # HTTP-only mode
                if region == 'us-east-1':
                    website_url = f"http://{bucket_name}.s3-website-{region}.amazonaws.com"
                else:
                    website_url = f"http://{bucket_name}.s3-website.{region}.amazonaws.com"
                
                return True, f"HTTP website configured. URL: {website_url}"
            
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
    
    def get_website_url(self, bucket_name: str, region: str = None, prefer_https: bool = True) -> Optional[str]:
        """Get website URL, preferring HTTPS CloudFront URL if available"""
        try:
            # First try to find existing CloudFront distribution for this bucket
            if prefer_https:
                try:
                    cloudfront = self.session.client('cloudfront')
                    distributions = cloudfront.list_distributions()
                    
                    # Always auto-detect the actual bucket region for S3 URL
                    s3 = self._get_s3_client()
                    location = s3.get_bucket_location(Bucket=bucket_name)
                    region = location.get('LocationConstraint') or 'us-east-1'
                    
                    # S3 website endpoint pattern
                    if region == 'us-east-1':
                        s3_origin = f"{bucket_name}.s3-website-{region}.amazonaws.com"
                    else:
                        s3_origin = f"{bucket_name}.s3-website.{region}.amazonaws.com"
                    
                    # Look for distribution pointing to this bucket
                    for dist in distributions.get('DistributionList', {}).get('Items', []):
                        for origin in dist.get('Origins', {}).get('Items', []):
                            if origin.get('DomainName') == s3_origin:
                                # Found CloudFront distribution
                                return f"https://{dist['DomainName']}"
                    
                except Exception as cf_error:
                    print(f"CloudFront lookup failed: {cf_error}")
            
            # Fallback to S3 website URL (HTTP only)
            s3 = self._get_s3_client()
            location = s3.get_bucket_location(Bucket=bucket_name)
            region = location.get('LocationConstraint') or 'us-east-1'
            
            # Generate S3 website URL based on region
            if region == 'us-east-1':
                return f"http://{bucket_name}.s3-website-{region}.amazonaws.com"
            else:
                return f"http://{bucket_name}.s3-website.{region}.amazonaws.com"
            
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

    def create_cloudfront_invalidation(
        self,
        distribution_id: str,
        paths: List[str] = None
    ) -> Tuple[bool, str, str]:
        """
        Create CloudFront cache invalidation for specified paths.

        Args:
            distribution_id: CloudFront distribution ID
            paths: List of paths to invalidate (default: ['/*'] for all files)

        Returns:
            Tuple[bool, str, str]: (success, message, invalidation_id)
        """
        if paths is None:
            paths = ['/*']

        try:
            cloudfront = self.session.client('cloudfront')

            # Create unique caller reference using timestamp
            caller_reference = f"invalidation-{int(datetime.now().timestamp())}"

            # Create invalidation
            response = cloudfront.create_invalidation(
                DistributionId=distribution_id,
                InvalidationBatch={
                    'Paths': {
                        'Quantity': len(paths),
                        'Items': paths
                    },
                    'CallerReference': caller_reference
                }
            )

            invalidation_id = response['Invalidation']['Id']
            status = response['Invalidation']['Status']

            return True, f"Invalidation created (ID: {invalidation_id}, Status: {status})", invalidation_id

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            return False, f"CloudFront invalidation failed ({error_code}): {str(e)}", ""
        except Exception as e:
            return False, f"CloudFront invalidation failed: {str(e)}", ""

    def update_cloudfront_origin_path(
        self,
        distribution_id: str,
        origin_path: str
    ) -> Tuple[bool, str]:
        """
        Update CloudFront distribution origin path to serve from S3 subdirectory.

        Args:
            distribution_id: CloudFront distribution ID
            origin_path: S3 directory path (e.g., '/client-name' or '' for root)

        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            cloudfront = self.session.client('cloudfront')

            # Get current distribution configuration
            response = cloudfront.get_distribution_config(Id=distribution_id)
            config = response['DistributionConfig']
            etag = response['ETag']

            # Update origin path for the first origin (S3 bucket)
            if config['Origins']['Quantity'] > 0:
                # Ensure origin_path starts with / if not empty
                if origin_path and not origin_path.startswith('/'):
                    origin_path = f'/{origin_path}'

                # Remove trailing slash if present
                origin_path = origin_path.rstrip('/')

                config['Origins']['Items'][0]['OriginPath'] = origin_path

                # Update the distribution
                cloudfront.update_distribution(
                    Id=distribution_id,
                    DistributionConfig=config,
                    IfMatch=etag
                )

                path_display = origin_path if origin_path else '/ (root)'
                return True, f"CloudFront origin path updated to: {path_display}"
            else:
                return False, "No origins found in CloudFront distribution"

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            return False, f"CloudFront update failed ({error_code}): {str(e)}"
        except Exception as e:
            return False, f"CloudFront update failed: {str(e)}"

    def find_distribution_by_origin(
        self,
        bucket_name: str,
        origin_path: str = ""
    ) -> Optional[str]:
        """
        Find existing CloudFront distribution for bucket and origin path.

        Args:
            bucket_name: S3 bucket name
            origin_path: Origin path (directory) within bucket (e.g., 'clean-restroom-rentals-va')

        Returns:
            Distribution ID if found, None otherwise
        """
        try:
            cloudfront = self.session.client('cloudfront')

            # Normalize origin path (should start with / if not empty)
            if origin_path and not origin_path.startswith('/'):
                origin_path = f'/{origin_path}'
            origin_path = origin_path.rstrip('/')  # Remove trailing slash

            # Get bucket region for origin domain
            try:
                s3 = self._get_s3_client()
                bucket_location = s3.get_bucket_location(Bucket=bucket_name)
                region = bucket_location.get('LocationConstraint') or 'us-east-1'
            except:
                region = 'us-east-1'

            # S3 origin domain name
            origin_domain = f"{bucket_name}.s3.{region}.amazonaws.com"

            # List all distributions
            paginator = cloudfront.get_paginator('list_distributions')
            for page in paginator.paginate():
                if 'Items' not in page['DistributionList']:
                    continue

                for dist in page['DistributionList']['Items']:
                    # Check each origin in the distribution
                    for origin in dist['Origins']['Items']:
                        # Match by domain name and origin path
                        if origin['DomainName'] == origin_domain:
                            dist_origin_path = origin.get('OriginPath', '')
                            if dist_origin_path == origin_path:
                                return dist['Id']

            return None

        except Exception as e:
            print(f"Error finding CloudFront distribution: {e}")
            return None

    def create_origin_access_control(
        self,
        name: str,
        description: str = ""
    ) -> Tuple[bool, Optional[str], str]:
        """
        Create CloudFront Origin Access Control (OAC) identity.

        Args:
            name: OAC name (should be unique)
            description: Optional description

        Returns:
            Tuple[bool, Optional[str], str]: (success, oac_id, message)
        """
        try:
            cloudfront = self.session.client('cloudfront')

            # Create OAC
            response = cloudfront.create_origin_access_control(
                OriginAccessControlConfig={
                    'Name': name,
                    'Description': description or f"OAC for {name}",
                    'SigningProtocol': 'sigv4',
                    'SigningBehavior': 'always',
                    'OriginAccessControlOriginType': 's3'
                }
            )

            oac_id = response['OriginAccessControl']['Id']
            return True, oac_id, f"OAC created: {oac_id}"

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            if error_code == 'OriginAccessControlAlreadyExists':
                # Try to find existing OAC
                try:
                    paginator = cloudfront.get_paginator('list_origin_access_controls')
                    for page in paginator.paginate():
                        if 'Items' in page['OriginAccessControlList']:
                            for oac in page['OriginAccessControlList']['Items']:
                                if oac['Name'] == name:
                                    return True, oac['Id'], f"Using existing OAC: {oac['Id']}"
                except:
                    pass

            return False, None, f"OAC creation failed ({error_code}): {str(e)}"
        except Exception as e:
            return False, None, f"OAC creation failed: {str(e)}"

    def create_cloudfront_distribution_with_oac(
        self,
        bucket_name: str,
        origin_path: str = "",
        comment: str = ""
    ) -> Tuple[bool, Optional[str], Optional[str], str]:
        """
        Create CloudFront distribution with Origin Access Control (OAC) for private S3 bucket.

        Args:
            bucket_name: S3 bucket name
            origin_path: S3 directory path (e.g., 'clean-restroom-rentals-va' or '' for root)
            comment: Distribution comment/description

        Returns:
            Tuple[bool, Optional[str], Optional[str], str]:
                (success, distribution_id, cloudfront_domain, message)
        """
        try:
            cloudfront = self.session.client('cloudfront')

            # Get bucket region
            try:
                s3 = self._get_s3_client()
                bucket_location = s3.get_bucket_location(Bucket=bucket_name)
                region = bucket_location.get('LocationConstraint') or 'us-east-1'
            except:
                region = 'us-east-1'

            # Normalize origin path
            if origin_path and not origin_path.startswith('/'):
                origin_path = f'/{origin_path}'
            origin_path = origin_path.rstrip('/')

            # S3 origin domain
            origin_domain = f"{bucket_name}.s3.{region}.amazonaws.com"

            # Create OAC
            oac_name = f"OAC-{bucket_name}-{origin_path.replace('/', '-') if origin_path else 'root'}"
            oac_success, oac_id, oac_message = self.create_origin_access_control(
                name=oac_name,
                description=f"OAC for {bucket_name}{origin_path}"
            )

            if not oac_success or not oac_id:
                return False, None, None, f"Failed to create OAC: {oac_message}"

            # Generate unique caller reference
            import time
            caller_reference = f"{bucket_name}-{origin_path}-{int(time.time())}"

            # Distribution configuration
            dist_config = {
                'CallerReference': caller_reference,
                'Comment': comment or f"Auto-created for {bucket_name}{origin_path}",
                'Enabled': True,
                'Origins': {
                    'Quantity': 1,
                    'Items': [
                        {
                            'Id': 'S3-Origin',
                            'DomainName': origin_domain,
                            'OriginPath': origin_path,
                            'OriginAccessControlId': oac_id,
                            'S3OriginConfig': {
                                'OriginAccessIdentity': ''  # Empty for OAC
                            }
                        }
                    ]
                },
                'DefaultCacheBehavior': {
                    'TargetOriginId': 'S3-Origin',
                    'ViewerProtocolPolicy': 'redirect-to-https',
                    'AllowedMethods': {
                        'Quantity': 2,
                        'Items': ['GET', 'HEAD'],
                        'CachedMethods': {
                            'Quantity': 2,
                            'Items': ['GET', 'HEAD']
                        }
                    },
                    'Compress': True,
                    'ForwardedValues': {
                        'QueryString': False,
                        'Cookies': {'Forward': 'none'}
                    },
                    'MinTTL': 0,
                    'DefaultTTL': 86400,
                    'MaxTTL': 31536000
                },
                'DefaultRootObject': 'index.html',
                'CustomErrorResponses': {
                    'Quantity': 1,
                    'Items': [
                        {
                            'ErrorCode': 404,
                            'ResponsePagePath': '/404.html',
                            'ResponseCode': '404',
                            'ErrorCachingMinTTL': 300
                        }
                    ]
                }
            }

            # Create distribution
            response = cloudfront.create_distribution(
                DistributionConfig=dist_config
            )

            distribution_id = response['Distribution']['Id']
            cloudfront_domain = response['Distribution']['DomainName']

            # Update S3 bucket policy to allow OAC
            policy_success, policy_message = self.update_bucket_policy_for_oac(
                bucket_name=bucket_name,
                distribution_arn=response['Distribution']['ARN']
            )

            if not policy_success:
                print(f"Warning: Bucket policy update failed: {policy_message}")

            return True, distribution_id, cloudfront_domain, \
                   f"CloudFront distribution created: {distribution_id} (domain: {cloudfront_domain})"

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            return False, None, None, f"CloudFront creation failed ({error_code}): {str(e)}"
        except Exception as e:
            return False, None, None, f"CloudFront creation failed: {str(e)}"

    def update_bucket_policy_for_oac(
        self,
        bucket_name: str,
        distribution_arn: str
    ) -> Tuple[bool, str]:
        """
        Update S3 bucket policy to allow CloudFront OAC access.

        Args:
            bucket_name: S3 bucket name
            distribution_arn: CloudFront distribution ARN

        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            s3 = self._get_s3_client()

            # Bucket policy allowing CloudFront OAC
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "AllowCloudFrontServicePrincipal",
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "cloudfront.amazonaws.com"
                        },
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{bucket_name}/*",
                        "Condition": {
                            "StringEquals": {
                                "AWS:SourceArn": distribution_arn
                            }
                        }
                    }
                ]
            }

            # Apply bucket policy
            s3.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(policy)
            )

            # Block public access (bucket should be private)
            try:
                s3.put_public_access_block(
                    Bucket=bucket_name,
                    PublicAccessBlockConfiguration={
                        'BlockPublicAcls': True,
                        'IgnorePublicAcls': True,
                        'BlockPublicPolicy': True,
                        'RestrictPublicBuckets': True
                    }
                )
            except:
                pass  # May not have permission, but policy is more important

            return True, f"Bucket policy updated for OAC access"

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            return False, f"Bucket policy update failed ({error_code}): {str(e)}"
        except Exception as e:
            return False, f"Bucket policy update failed: {str(e)}"

    def get_or_create_distribution(
        self,
        bucket_name: str,
        origin_path: str = "",
        comment: str = ""
    ) -> Tuple[bool, Optional[str], Optional[str], bool, str]:
        """
        Get existing CloudFront distribution or create new one with OAC.

        High-level convenience method that:
        1. Searches for existing distribution matching bucket + origin path
        2. If found, returns existing distribution
        3. If not found, creates new distribution with OAC

        Args:
            bucket_name: S3 bucket name
            origin_path: Directory/prefix within bucket (e.g., "my-client" or "")
            comment: Optional description for distribution (used if creating new)

        Returns:
            Tuple of (success, distribution_id, cloudfront_domain, is_new, message)
            - success: True if distribution available (found or created)
            - distribution_id: CloudFront distribution ID (e.g., "E1234567890ABC")
            - cloudfront_domain: CloudFront domain (e.g., "d111111abcdef8.cloudfront.net")
            - is_new: True if created new, False if reused existing
            - message: Status or error message

        Example:
            success, dist_id, domain, is_new, msg = s3_manager.get_or_create_distribution(
                bucket_name="my-bucket",
                origin_path="my-client",
                comment="Auto-created for My Client"
            )
            if success:
                url = f"https://{domain}/my-client"
        """
        try:
            # Step 1: Check for existing distribution
            existing_dist_id = self.find_distribution_by_origin(
                bucket_name=bucket_name,
                origin_path=origin_path
            )

            if existing_dist_id:
                # Found existing distribution - get its domain
                cloudfront = self.session.client('cloudfront')
                response = cloudfront.get_distribution(Id=existing_dist_id)
                cloudfront_domain = response['Distribution']['DomainName']

                return True, existing_dist_id, cloudfront_domain, False, \
                       f"Reusing existing distribution: {existing_dist_id}"

            # Step 2: No existing distribution, create new one
            create_success, dist_id, domain, create_message = \
                self.create_cloudfront_distribution_with_oac(
                    bucket_name=bucket_name,
                    origin_path=origin_path,
                    comment=comment
                )

            if create_success:
                return True, dist_id, domain, True, \
                       f"Created new distribution: {dist_id}"
            else:
                return False, None, None, False, \
                       f"Failed to create distribution: {create_message}"

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            return False, None, None, False, \
                   f"Distribution lookup/create failed ({error_code}): {str(e)}"
        except Exception as e:
            return False, None, None, False, \
                   f"Distribution lookup/create failed: {str(e)}"

    def check_distribution_oac_status(
        self,
        distribution_id: str
    ) -> Tuple[bool, bool, str]:
        """
        Check if CloudFront distribution has Origin Access Control (OAC) configured.

        Args:
            distribution_id: CloudFront distribution ID

        Returns:
            Tuple of (success, has_oac, message)
            - success: True if check completed (even if no OAC found)
            - has_oac: True if distribution uses OAC, False otherwise
            - message: Description of OAC status or error message

        Example:
            success, has_oac, msg = s3_manager.check_distribution_oac_status("E1234567890ABC")
            if success and not has_oac:
                print("WARNING: Distribution lacks OAC - will cause 403 errors with private bucket")
        """
        try:
            cloudfront = self.session.client('cloudfront')

            # Get distribution configuration
            response = cloudfront.get_distribution_config(Id=distribution_id)
            config = response['DistributionConfig']

            # Check if any origin has OAC configured
            has_oac = False
            oac_count = 0

            if 'Origins' in config and 'Items' in config['Origins']:
                for origin in config['Origins']['Items']:
                    # Check for OriginAccessControlId (OAC)
                    if origin.get('OriginAccessControlId'):
                        has_oac = True
                        oac_count += 1

            if has_oac:
                return True, True, f"Distribution has OAC configured ({oac_count} origin(s) with OAC)"
            else:
                return True, False, \
                    "Distribution does NOT have OAC - uses legacy Origin Access Identity or public access"

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            if error_code == 'NoSuchDistribution':
                return False, False, f"Distribution not found: {distribution_id}"
            return False, False, f"OAC check failed ({error_code}): {str(e)}"
        except Exception as e:
            return False, False, f"OAC check failed: {str(e)}"

    def disable_distribution(
        self,
        distribution_id: str
    ) -> Tuple[bool, str]:
        """
        Disable CloudFront distribution (prerequisite for deletion).

        Args:
            distribution_id: CloudFront distribution ID

        Returns:
            Tuple of (success, message)
        """
        try:
            cloudfront = self.session.client('cloudfront')

            # Get current config and ETag
            response = cloudfront.get_distribution_config(Id=distribution_id)
            config = response['DistributionConfig']
            etag = response['ETag']

            # Check if already disabled
            if not config['Enabled']:
                return True, f"Distribution already disabled: {distribution_id}"

            # Disable distribution
            config['Enabled'] = False

            cloudfront.update_distribution(
                Id=distribution_id,
                DistributionConfig=config,
                IfMatch=etag
            )

            return True, \
                f"Distribution disabled: {distribution_id}. " \
                f"Wait for status 'Deployed' before deleting (may take 5-10 minutes)."

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            return False, f"Disable failed ({error_code}): {str(e)}"
        except Exception as e:
            return False, f"Disable failed: {str(e)}"

    def delete_distribution(
        self,
        distribution_id: str
    ) -> Tuple[bool, str]:
        """
        Delete CloudFront distribution (must be disabled first).

        Args:
            distribution_id: CloudFront distribution ID

        Returns:
            Tuple of (success, message)
        """
        try:
            cloudfront = self.session.client('cloudfront')

            # Get current config and ETag
            response = cloudfront.get_distribution_config(Id=distribution_id)
            config = response['DistributionConfig']
            etag = response['ETag']

            # Verify distribution is disabled
            if config['Enabled']:
                return False, \
                    f"Cannot delete: Distribution is still enabled. " \
                    f"Disable it first using disable_distribution()."

            # Check deployment status
            dist_response = cloudfront.get_distribution(Id=distribution_id)
            status = dist_response['Distribution']['Status']

            if status != 'Deployed':
                return False, \
                    f"Cannot delete: Distribution status is '{status}'. " \
                    f"Wait until status is 'Deployed' (current changes must finish deploying)."

            # Delete distribution
            cloudfront.delete_distribution(
                Id=distribution_id,
                IfMatch=etag
            )

            return True, f"Distribution deleted: {distribution_id}"

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            return False, f"Delete failed ({error_code}): {str(e)}"
        except Exception as e:
            return False, f"Delete failed: {str(e)}"

    def _get_file_metadata(self, file_ext: str) -> Dict[str, str]:
        """Get S3 upload metadata for file extension"""
        if file_ext in self.cache_settings:
            return self.cache_settings[file_ext]
        
        # Default for unknown file types
        content_type, _ = mimetypes.guess_type(f"file.{file_ext}")
        return {
            'CacheControl': 'max-age=86400,public',
            'ContentType': content_type or 'application/octet-stream'
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
        
        # SOP allows any valid bucket name - users should replace 'client-website-*' with their preferred naming convention
        # Only enforce AWS S3 bucket naming rules, not specific patterns
        
        return True, "Bucket name is valid"