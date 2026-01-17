"""
Module/Script Name: Asset Uploader
Path: src/core/deployment/asset_uploader.py

Description:
Unified asset upload interface for uploading arbitrary files (Excel, PDF, Word, etc.)
to cloud storage (AWS S3, Google GCS). Generates public URLs for uploaded assets.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-01-17

Last Modified Date:
2025-01-17

Version: 1.00

Comments:
* v1.00 - Initial implementation with S3 and GCS support
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Callable, List
from datetime import datetime
import mimetypes

from ..aws.s3_manager import S3Manager
from ..deployment.providers.gcs_provider import GCSProvider
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class UploadResult:
    """Result of an asset upload operation"""
    filename: str
    size_bytes: int
    file_type: str
    public_url: str
    bucket: str
    remote_path: str
    region: str
    provider: str
    uploaded_at: datetime
    success: bool
    error_message: Optional[str] = None


class AssetUploader:
    """
    Unified interface for uploading assets to cloud storage.

    Supports:
    - AWS S3
    - Google Cloud Storage
    """

    # Supported file extensions
    SUPPORTED_EXTENSIONS = {
        '.xlsx', '.xls',  # Excel
        '.pdf',  # PDF
        '.docx', '.doc',  # Word
        '.html', '.htm',  # HTML
        '.xml',  # XML
        '.txt', '.csv', '.json',  # Text files
        '.zip', '.tar', '.gz'  # Archives
    }

    # Default max file size: 100 MB
    DEFAULT_MAX_SIZE_MB = 100

    def __init__(self, provider_type: str, credentials: dict):
        """
        Initialize asset uploader.

        Args:
            provider_type: 'aws_s3' or 'google_gcs'
            credentials: Provider-specific credentials dict
        """
        self.provider_type = provider_type
        self.credentials = credentials
        self._client = None

    def _get_client(self):
        """Get or create cloud provider client"""
        if self._client:
            return self._client

        if self.provider_type == 'aws_s3':
            # S3Manager expects profile_name or session
            self._client = S3Manager(profile_name=self.credentials.get('profile_name'))
        elif self.provider_type == 'google_gcs':
            # GCSProvider expects project_id and service_account_json
            self._client = GCSProvider(
                project_id=self.credentials.get('project_id'),
                service_account_json=self.credentials.get('service_account_json')
            )
        else:
            raise ValueError(f"Unsupported provider: {self.provider_type}")

        return self._client

    def validate_file(self, file_path: Path, max_size_mb: int = None) -> tuple[bool, str]:
        """
        Validate file before upload.

        Args:
            file_path: Path to file
            max_size_mb: Maximum file size in MB

        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        if max_size_mb is None:
            max_size_mb = self.DEFAULT_MAX_SIZE_MB

        # Check file exists
        if not file_path.exists():
            return False, f"File not found: {file_path}"

        # Check file size
        size_bytes = file_path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)

        if size_mb > max_size_mb:
            return False, f"File too large: {size_mb:.1f}MB (max: {max_size_mb}MB)"

        # Check extension (optional - warn but don't reject)
        ext = file_path.suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            logger.warning(f"Uploading file with unsupported extension: {ext}")

        return True, ""

    def upload_file(self, local_file: Path, bucket: str, remote_path: str,
                   region: str = 'us-east-1') -> UploadResult:
        """
        Upload single file to cloud storage.

        Args:
            local_file: Local file path
            bucket: Bucket name
            remote_path: Remote path/key (e.g., 'assets/document.pdf')
            region: Cloud region

        Returns:
            UploadResult: Upload result with public URL
        """
        # Validate file
        is_valid, error_msg = self.validate_file(local_file)
        if not is_valid:
            return UploadResult(
                filename=local_file.name,
                size_bytes=0,
                file_type='',
                public_url='',
                bucket=bucket,
                remote_path=remote_path,
                region=region,
                provider=self.provider_type,
                uploaded_at=datetime.now(),
                success=False,
                error_message=error_msg
            )

        # Get file metadata
        size_bytes = local_file.stat().st_size
        file_type, _ = mimetypes.guess_type(str(local_file))
        file_type = file_type or 'application/octet-stream'

        try:
            client = self._get_client()

            if self.provider_type == 'aws_s3':
                # Upload to S3 with public-read ACL
                import boto3
                s3_client = boto3.client('s3', region_name=region)

                s3_client.upload_file(
                    str(local_file),
                    bucket,
                    remote_path,
                    ExtraArgs={
                        'ContentType': file_type,
                        'ACL': 'public-read'
                    }
                )

                # Generate public URL
                public_url = f"https://{bucket}.s3.{region}.amazonaws.com/{remote_path}"

            elif self.provider_type == 'google_gcs':
                # Upload to GCS
                from google.cloud import storage

                storage_client = storage.Client(project=self.credentials.get('project_id'))
                bucket_obj = storage_client.bucket(bucket)
                blob = bucket_obj.blob(remote_path)

                blob.upload_from_filename(
                    str(local_file),
                    content_type=file_type
                )

                # Make blob publicly accessible
                blob.make_public()

                # Generate public URL
                public_url = f"https://storage.googleapis.com/{bucket}/{remote_path}"

            else:
                raise ValueError(f"Unsupported provider: {self.provider_type}")

            logger.info(f"Uploaded: {local_file.name} -> {public_url}")

            return UploadResult(
                filename=local_file.name,
                size_bytes=size_bytes,
                file_type=file_type,
                public_url=public_url,
                bucket=bucket,
                remote_path=remote_path,
                region=region,
                provider=self.provider_type,
                uploaded_at=datetime.now(),
                success=True
            )

        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return UploadResult(
                filename=local_file.name,
                size_bytes=size_bytes,
                file_type=file_type,
                public_url='',
                bucket=bucket,
                remote_path=remote_path,
                region=region,
                provider=self.provider_type,
                uploaded_at=datetime.now(),
                success=False,
                error_message=str(e)
            )

    def upload_files_batch(self, files: List[Path], bucket: str, prefix: str,
                          region: str = 'us-east-1',
                          progress_callback: Optional[Callable[[int, int, str], None]] = None) -> List[UploadResult]:
        """
        Upload multiple files to cloud storage.

        Args:
            files: List of file paths
            bucket: Bucket name
            prefix: Remote prefix (e.g., 'assets/')
            region: Cloud region
            progress_callback: Callback(current, total, filename)

        Returns:
            List[UploadResult]: Results for each file
        """
        results = []
        total = len(files)

        for i, file_path in enumerate(files, 1):
            # Generate remote path
            remote_path = f"{prefix.rstrip('/')}/{file_path.name}"

            # Progress callback
            if progress_callback:
                progress_callback(i, total, file_path.name)

            # Upload file
            result = self.upload_file(file_path, bucket, remote_path, region)
            results.append(result)

        return results

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size for display.

        Args:
            size_bytes: Size in bytes

        Returns:
            str: Formatted size (e.g., '1.5 MB')
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
