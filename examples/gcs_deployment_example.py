"""
Module/Script Name: GCS Deployment Example
Path: examples/gcs_deployment_example.py

Description:
Example script demonstrating Google Cloud Storage deployment using the
multi-cloud provider architecture.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-11-19

Last Modified Date:
2025-11-19

Comments:
* v1.00 - Initial GCS deployment example
"""

from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.deployment.providers import (
    GCSProvider,
    ProviderConfig,
    ProviderType,
    DeploymentMode,
)


def example_1_basic_deployment():
    """
    Example 1: Basic GCS Deployment

    This example demonstrates:
    - Authentication with service account
    - Bucket creation
    - Website hosting configuration
    - Directory upload
    """
    print("=" * 60)
    print("Example 1: Basic GCS Deployment")
    print("=" * 60)

    # Configure provider
    config = ProviderConfig(
        provider_type=ProviderType.GOOGLE_GCS,
        credentials={
            # Option 1: Service Account JSON file
            "service_account_json": "/path/to/gcs-deployer-key.json",

            # Option 2: Service Account Key Components
            # "project_id": "my-gcp-project",
            # "client_email": "deployer@my-gcp-project.iam.gserviceaccount.com",
            # "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"

            # Option 3: Application Default Credentials
            # "use_adc": True
        },
        region="us-central1",
        deployment_mode=DeploymentMode.STORAGE_ONLY
    )

    print(f"\nProvider: {config.provider_type.value}")
    print(f"Region: {config.region}")
    print(f"Mode: {config.deployment_mode.value}")

    # Create provider instance
    provider = GCSProvider(config)

    # Authenticate
    print("\nAuthenticating...")
    try:
        if provider.authenticate():
            print("Authentication successful!")
            print(f"Project ID: {provider.project_id}")

            # Test connection
            print("\nTesting connection...")
            success, message = provider.test_connection()
            print(message)

            if success:
                # Create bucket
                bucket_name = "my-test-website-bucket-12345"  # Must be globally unique
                print(f"\nCreating bucket: {bucket_name}...")

                if provider.create_bucket(bucket_name):
                    print("Bucket created successfully!")

                    # Configure for website hosting
                    print("\nConfiguring website hosting...")
                    if provider.configure_website_hosting(bucket_name):
                        print("Website hosting configured!")

                        # Upload website files
                        website_dir = Path("./output/test-website")

                        if website_dir.exists():
                            print(f"\nUploading files from: {website_dir}")

                            result = provider.upload_directory(
                                website_dir,
                                bucket_name,
                                progress_callback=lambda c, t, f: print(f"[{c}/{t}] {f}")
                            )

                            print("\n" + "=" * 60)
                            print("Deployment Result:")
                            print("=" * 60)
                            print(result)

                            if result.success:
                                print(f"\nWebsite URL: {result.website_url}")
                        else:
                            print(f"Website directory not found: {website_dir}")
                            print("Skipping upload...")

    except Exception as e:
        print(f"Error: {str(e)}")


def example_2_list_buckets():
    """
    Example 2: List All Buckets

    This example demonstrates:
    - Listing all buckets in the project
    """
    print("\n" + "=" * 60)
    print("Example 2: List All Buckets")
    print("=" * 60)

    config = ProviderConfig(
        provider_type=ProviderType.GOOGLE_GCS,
        credentials={
            "service_account_json": "/path/to/gcs-deployer-key.json"
        },
        region="us-central1"
    )

    provider = GCSProvider(config)

    if provider.authenticate():
        print(f"\nListing buckets in project: {provider.project_id}")

        buckets = provider.list_buckets()

        if buckets:
            print(f"\nFound {len(buckets)} bucket(s):")
            for i, bucket in enumerate(buckets, 1):
                print(f"  {i}. {bucket}")
        else:
            print("\nNo buckets found.")


def example_3_progress_tracking():
    """
    Example 3: Deployment with Detailed Progress Tracking

    This example demonstrates:
    - Custom progress callback
    - Percentage calculation
    - File-by-file tracking
    """
    print("\n" + "=" * 60)
    print("Example 3: Deployment with Progress Tracking")
    print("=" * 60)

    def detailed_progress(current, total, filename):
        """Detailed progress callback"""
        percent = (current / total) * 100
        bar_length = 40
        filled = int(bar_length * current / total)
        bar = "+" * filled + "-" * (bar_length - filled)

        print(f"\r[{bar}] {percent:5.1f}% ({current}/{total}) - {filename[:30]:<30}", end="")

        if current == total:
            print()  # New line at end

    config = ProviderConfig(
        provider_type=ProviderType.GOOGLE_GCS,
        credentials={
            "service_account_json": "/path/to/gcs-deployer-key.json"
        },
        region="us-central1"
    )

    provider = GCSProvider(config)

    if provider.authenticate():
        bucket_name = "my-progress-test-bucket"

        provider.create_bucket(bucket_name)
        provider.configure_website_hosting(bucket_name)

        website_dir = Path("./output/test-website")

        if website_dir.exists():
            print(f"\nUploading from: {website_dir}")
            print("Progress:")

            result = provider.upload_directory(
                website_dir,
                bucket_name,
                progress_callback=detailed_progress
            )

            print(f"\nDeployment {'succeeded' if result.success else 'failed'}!")
            print(f"Files uploaded: {result.files_uploaded}")

            if result.errors:
                print(f"\nErrors encountered: {len(result.errors)}")
                for error in result.errors[:5]:  # Show first 5 errors
                    print(f"  - {error}")


def example_4_multi_region():
    """
    Example 4: Deploy to Multiple Regions

    This example demonstrates:
    - Multi-region deployment
    - Redundancy setup
    - Regional URLs
    """
    print("\n" + "=" * 60)
    print("Example 4: Multi-Region Deployment")
    print("=" * 60)

    regions = [
        ("us", "United States"),
        ("eu", "European Union"),
        ("asia", "Asia Pacific")
    ]

    website_dir = Path("./output/test-website")

    if not website_dir.exists():
        print(f"Website directory not found: {website_dir}")
        return

    print(f"\nDeploying to {len(regions)} regions...")

    results = {}

    for region_code, region_name in regions:
        print(f"\n{'=' * 40}")
        print(f"Deploying to {region_name} ({region_code})")
        print("=" * 40)

        config = ProviderConfig(
            provider_type=ProviderType.GOOGLE_GCS,
            credentials={
                "service_account_json": "/path/to/gcs-deployer-key.json"
            },
            region=region_code
        )

        provider = GCSProvider(config)

        if provider.authenticate():
            bucket_name = f"my-website-{region_code}"

            provider.create_bucket(bucket_name)
            provider.configure_website_hosting(bucket_name)

            result = provider.upload_directory(
                website_dir,
                bucket_name
            )

            results[region_code] = result

            if result.success:
                print("Deployment successful!")
                print(f"Files: {result.files_uploaded}")
                print(f"URL: {result.website_url}")
            else:
                print("Deployment failed!")
                print(f"Errors: {len(result.errors)}")

    # Summary
    print("\n" + "=" * 60)
    print("Multi-Region Deployment Summary")
    print("=" * 60)

    for region_code, region_name in regions:
        if region_code in results:
            result = results[region_code]
            status = "SUCCESS" if result.success else "FAILED"
            print(f"\n{region_name} ({region_code}): {status}")
            if result.success:
                print(f"  URL: {result.website_url}")
                print(f"  Files: {result.files_uploaded}")


def main():
    """Main function to run examples"""
    print("\nGCS Deployment Examples")
    print("Note: Update the service account path before running")
    print()

    # Run examples
    # Uncomment the examples you want to run:

    # example_1_basic_deployment()
    # example_2_list_buckets()
    # example_3_progress_tracking()
    # example_4_multi_region()

    print("\nUpdate the service account path and uncomment examples to run them.")


if __name__ == "__main__":
    main()
