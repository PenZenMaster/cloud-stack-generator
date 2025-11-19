"""
Module/Script Name: S3 Website Deployer
Path: src/core/deployment/s3_deployer.py

Description:
Programmatically creates S3 buckets, configures them for static website hosting,
and deploys generated website files with proper public access settings.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-11-12

Last Modified Date:
2025-11-12

Comments:
* v1.00 - Initial implementation with full bucket creation and configuration
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any

import boto3
from botocore.exceptions import ClientError

from ..utils.logger import get_logger

# Initialize module logger
logger = get_logger(__name__)


class S3WebsiteDeployer:
    """Handles S3 bucket creation, configuration, and website deployment."""

    def __init__(self, profile_name: str = "AWS", region: str = "us-east-1"):
        """
        Initialize the S3 deployer with AWS credentials.

        Args:
            profile_name: AWS CLI profile name to use
            region: AWS region for bucket operations
        """
        self.session = boto3.Session(profile_name=profile_name, region_name=region)
        self.s3_client = self.session.client("s3")
        self.s3_resource = self.session.resource("s3")
        self.region = region

    def create_bucket(self, bucket_name: str) -> bool:
        """
        Create an S3 bucket if it doesn't already exist.

        Args:
            bucket_name: Name of the bucket to create

        Returns:
            True if bucket was created or already exists, False on error
        """
        try:
            # Check if bucket already exists
            self.s3_client.head_bucket(Bucket=bucket_name)
            logger.info(f"Bucket {bucket_name} already exists")
            return True
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                # Bucket doesn't exist, create it
                try:
                    if self.region == "us-east-1":
                        # us-east-1 doesn't require LocationConstraint
                        self.s3_client.create_bucket(Bucket=bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=bucket_name,
                            CreateBucketConfiguration={"LocationConstraint": self.region},
                        )
                    logger.info(f"Successfully created bucket: {bucket_name}")
                    return True
                except ClientError as create_error:
                    logger.error(f"Failed to create bucket {bucket_name}: {create_error}")
                    return False
            else:
                logger.error(f"Error checking bucket {bucket_name}: {e}")
                return False

    def configure_public_access(self, bucket_name: str) -> bool:
        """
        Disable public access block settings to allow public website hosting.

        Args:
            bucket_name: Name of the bucket to configure

        Returns:
            True if configuration succeeded, False otherwise
        """
        try:
            self.s3_client.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    "BlockPublicAcls": False,
                    "IgnorePublicAcls": False,
                    "BlockPublicPolicy": False,
                    "RestrictPublicBuckets": False,
                },
            )
            logger.info(f"Disabled public access block for {bucket_name}")
            return True
        except ClientError as e:
            logger.error(f"Failed to configure public access for {bucket_name}: {e}")
            return False

    def apply_public_read_policy(self, bucket_name: str) -> bool:
        """
        Apply a bucket policy that allows public read access to all objects.

        Args:
            bucket_name: Name of the bucket to apply policy to

        Returns:
            True if policy was applied, False otherwise
        """
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*",
                }
            ],
        }

        try:
            self.s3_client.put_bucket_policy(
                Bucket=bucket_name, Policy=json.dumps(bucket_policy)
            )
            logger.info(f"Applied public read policy to {bucket_name}")
            return True
        except ClientError as e:
            logger.error(f"Failed to apply bucket policy to {bucket_name}: {e}")
            return False

    def enable_static_website(
        self,
        bucket_name: str,
        index_document: str = "index.html",
        error_document: str = "error.html",
    ) -> bool:
        """
        Enable static website hosting on the bucket.

        Args:
            bucket_name: Name of the bucket to configure
            index_document: Default index document filename
            error_document: Error document filename

        Returns:
            True if website hosting was enabled, False otherwise
        """
        try:
            self.s3_client.put_bucket_website(
                Bucket=bucket_name,
                WebsiteConfiguration={
                    "IndexDocument": {"Suffix": index_document},
                    "ErrorDocument": {"Key": error_document},
                },
            )
            logger.info(f"Enabled static website hosting for {bucket_name}")
            return True
        except ClientError as e:
            logger.error(f"Failed to enable website hosting for {bucket_name}: {e}")
            return False

    def get_website_url(self, bucket_name: str) -> str:
        """
        Get the public website URL for a bucket.

        Args:
            bucket_name: Name of the bucket

        Returns:
            The HTTP website URL
        """
        return f"http://{bucket_name}.s3-website-{self.region}.amazonaws.com"

    def upload_directory(
        self, local_path: Path, bucket_name: str, prefix: str = ""
    ) -> bool:
        """
        Upload an entire directory to S3, maintaining directory structure.

        Args:
            local_path: Path to local directory to upload
            bucket_name: Target S3 bucket name
            prefix: Optional prefix (directory path) in the bucket

        Returns:
            True if upload succeeded, False otherwise
        """
        if not local_path.exists() or not local_path.is_dir():
            logger.error(f"Local path {local_path} does not exist or is not a directory")
            return False

        try:
            bucket = self.s3_resource.Bucket(bucket_name)
            files_uploaded = 0

            for file_path in local_path.rglob("*"):
                if file_path.is_file():
                    # Calculate relative path and S3 key
                    relative_path = file_path.relative_to(local_path)
                    s3_key = f"{prefix}/{relative_path}" if prefix else str(relative_path)
                    s3_key = s3_key.replace("\\", "/")  # Normalize path separators

                    # Determine content type
                    content_type = self._get_content_type(file_path)

                    # Prepare upload arguments with SEO-friendly headers
                    extra_args = {
                        "ContentType": content_type,
                        "CacheControl": "public, max-age=31536000" if file_path.suffix in [".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".woff", ".woff2"] else "public, max-age=3600",
                    }

                    # Upload file
                    bucket.upload_file(
                        str(file_path),
                        s3_key,
                        ExtraArgs=extra_args,
                    )
                    files_uploaded += 1
                    logger.debug(f"Uploaded {file_path} -> s3://{bucket_name}/{s3_key}")

            logger.info(f"Successfully uploaded {files_uploaded} files to {bucket_name}")
            return True

        except ClientError as e:
            logger.error(f"Failed to upload directory to {bucket_name}: {e}")
            return False

    def deploy_website(
        self,
        bucket_name: str,
        local_path: Path,
        subdirectory: Optional[str] = None,
        create_if_not_exists: bool = True,
    ) -> Dict[str, Any]:
        """
        Complete website deployment: create bucket, configure, and upload files.

        Args:
            bucket_name: Name of the S3 bucket
            local_path: Path to the generated website files
            subdirectory: Optional subdirectory within the bucket (e.g., "clean-restroom-rental-va")
            create_if_not_exists: Create and configure the bucket if it doesn't exist

        Returns:
            Dictionary with deployment results including success status and URLs
        """
        result = {
            "success": False,
            "bucket_name": bucket_name,
            "website_url": None,
            "full_url": None,
            "steps_completed": [],
            "errors": [],
        }

        try:
            # Step 1: Create bucket if needed
            if create_if_not_exists:
                if self.create_bucket(bucket_name):
                    result["steps_completed"].append("bucket_created")
                else:
                    result["errors"].append("Failed to create bucket")
                    return result

                # Step 2: Configure public access
                if self.configure_public_access(bucket_name):
                    result["steps_completed"].append("public_access_configured")
                else:
                    result["errors"].append("Failed to configure public access")
                    return result

                # Step 3: Apply public read policy
                if self.apply_public_read_policy(bucket_name):
                    result["steps_completed"].append("public_policy_applied")
                else:
                    result["errors"].append("Failed to apply public read policy")
                    return result

                # Step 4: Enable static website hosting
                if self.enable_static_website(bucket_name):
                    result["steps_completed"].append("website_hosting_enabled")
                else:
                    result["errors"].append("Failed to enable website hosting")
                    return result

            # Step 5: Upload files
            prefix = subdirectory if subdirectory else ""
            if self.upload_directory(local_path, bucket_name, prefix):
                result["steps_completed"].append("files_uploaded")
            else:
                result["errors"].append("Failed to upload files")
                return result

            # Success - generate URLs
            result["success"] = True
            result["website_url"] = self.get_website_url(bucket_name)
            if subdirectory:
                result["full_url"] = f"{result['website_url']}/{subdirectory}/"
            else:
                result["full_url"] = result["website_url"]

            logger.info(f"Successfully deployed website to {result['full_url']}")

        except Exception as e:
            logger.error(f"Deployment failed with unexpected error: {e}")
            result["errors"].append(str(e))

        return result

    @staticmethod
    def _get_content_type(file_path: Path) -> str:
        """
        Determine the content type based on file extension.

        Args:
            file_path: Path to the file

        Returns:
            MIME type string
        """
        extension = file_path.suffix.lower()
        content_types = {
            ".html": "text/html",
            ".css": "text/css",
            ".js": "application/javascript",
            ".json": "application/json",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".svg": "image/svg+xml",
            ".ico": "image/x-icon",
            ".woff": "font/woff",
            ".woff2": "font/woff2",
            ".ttf": "font/ttf",
            ".pdf": "application/pdf",
            ".txt": "text/plain",
            ".xml": "application/xml",
        }
        return content_types.get(extension, "application/octet-stream")


def deploy_client_website(
    client_slug: str,
    bucket_name: str = "sanitation-rentals",
    profile: str = "AWS",
    region: str = "us-east-1",
) -> Dict[str, Any]:
    """
    Convenience function to deploy a generated client website to S3.

    Args:
        client_slug: Client identifier matching local directory name (e.g., "clean_restroom_rental_va")
                     Will be converted to kebab-case for S3 (e.g., "clean-restroom-rental-va")
        bucket_name: S3 bucket name (must use kebab-case)
        profile: AWS CLI profile name
        region: AWS region

    Returns:
        Deployment result dictionary
    """
    # Determine local path (uses snake_case on filesystem)
    output_path = Path(__file__).parent.parent.parent.parent / "output" / "clients" / client_slug

    if not output_path.exists():
        logger.error(f"Client website not found at {output_path}")
        return {"success": False, "errors": [f"Website directory not found: {output_path}"]}

    # Convert to kebab-case for S3 URL-friendly naming
    s3_directory = client_slug.replace("_", "-")

    # Deploy
    deployer = S3WebsiteDeployer(profile_name=profile, region=region)
    result = deployer.deploy_website(
        bucket_name=bucket_name,
        local_path=output_path,
        subdirectory=s3_directory,
        create_if_not_exists=True,
    )

    # Log results
    if result["success"]:
        logger.info("Website deployed successfully!")
        logger.info(f"Bucket: {result['bucket_name']}")
        logger.info(f"Website URL: {result['full_url']}")
        logger.info(f"Steps completed: {', '.join(result['steps_completed'])}")
    else:
        logger.error("Deployment failed!")
        logger.error(f"Errors: {', '.join(result['errors'])}")

    return result


if __name__ == "__main__":
    # Example: Deploy Clean Restroom Rental VA website
    deploy_client_website("clean_restroom_rental_va")
