"""
List CloudFront distributions using app credentials

This script uses the same credential system as the Cloud Stack Generator app
to list all CloudFront distributions in your AWS account.
"""
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.aws.credentials import AWSCredentialsManager
from botocore.exceptions import ClientError


def list_distributions():
    """List all CloudFront distributions using app credentials"""
    try:
        # Initialize credentials manager (same as the app uses)
        creds_manager = AWSCredentialsManager()

        # Get available profiles
        if not creds_manager.profiles:
            print("ERROR: No AWS profiles configured in the app.")
            print("\nPlease configure an AWS profile in the app first:")
            print("1. Open the Cloud Stack Generator app")
            print("2. Go to the 'Cloud Deployment' tab")
            print("3. Click 'New Profile' and configure your AWS credentials")
            return False

        # Use active profile or first available
        profile_name = creds_manager.active_profile
        if not profile_name:
            profile_name = list(creds_manager.profiles.keys())[0]
            print(f"Using profile: {profile_name} (no active profile set)")
        else:
            print(f"Using active profile: {profile_name}")

        print("-" * 60)

        # Get session for the profile
        try:
            session = creds_manager._get_session(profile_name)
        except ValueError as e:
            print(f"ERROR: {e}")
            print("\nPlease reconfigure your AWS credentials in the app:")
            print("1. Open Cloud Stack Generator")
            print("2. Go to Cloud Deployment tab")
            print("3. Edit the profile and enter valid credentials")
            return False

        # List CloudFront distributions
        cloudfront = session.client('cloudfront')

        print("\nFetching CloudFront distributions...")
        try:
            response = cloudfront.list_distributions()
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            print(f"\nERROR: Failed to list CloudFront distributions ({error_code})")
            print(f"Details: {e}")

            if error_code == 'InvalidClientTokenId':
                print("\nYour AWS credentials appear to be invalid or expired.")
                print("Please update them in the app.")
            elif 'AccessDenied' in error_code:
                print("\nYour AWS credentials lack CloudFront permissions.")
                print("Required permission: cloudfront:ListDistributions")

            return False

        # Parse and display distributions
        if 'DistributionList' not in response or response['DistributionList']['Quantity'] == 0:
            print("\n" + "=" * 60)
            print("NO CLOUDFRONT DISTRIBUTIONS FOUND")
            print("=" * 60)
            print("\nYou need to create a CloudFront distribution first.")
            print("\nOption 1: Create via AWS Console")
            print("  1. Go to https://console.aws.amazon.com/cloudfront/")
            print("  2. Click 'Create Distribution'")
            print("  3. Configure:")
            print("     - Origin domain: portable-sanitation-solutions.s3.us-east-1.amazonaws.com")
            print("     - Origin path: Leave blank (app will auto-update)")
            print("     - Default root object: index.html")
            print("     - All other settings: defaults are fine")
            print("  4. Click 'Create Distribution'")
            print("  5. Copy the Distribution ID")
            print("  6. Enter it in the app's Cloud Deployment tab")
            print("\nOption 2: Create via AWS CLI")
            print("  aws cloudfront create-distribution --origin-domain-name \\")
            print("    portable-sanitation-solutions.s3.us-east-1.amazonaws.com \\")
            print("    --default-root-object index.html")
            return True

        # Display distributions
        distributions = response['DistributionList']['Items']
        print(f"\nFound {len(distributions)} CloudFront distribution(s):\n")
        print("=" * 60)

        for idx, dist in enumerate(distributions, 1):
            dist_id = dist['Id']
            domain = dist['DomainName']
            status = dist['Status']
            enabled = dist['Enabled']

            # Get origin details
            origins = dist['Origins']['Items']
            origin_domain = origins[0]['DomainName'] if origins else 'N/A'
            origin_path = origins[0].get('OriginPath', '') if origins else ''

            comment = dist.get('Comment', 'No description')

            print(f"\nDistribution #{idx}")
            print(f"  ID: {dist_id}")
            print(f"  Domain: {domain}")
            print(f"  Status: {status}")
            print(f"  Enabled: {enabled}")
            print(f"  Comment: {comment}")
            print(f"  Origin Domain: {origin_domain}")
            print(f"  Origin Path: '{origin_path}'")

            # Check if this might be the right one
            if 'portable-sanitation-solutions' in origin_domain:
                print(f"  >>> MATCH: This distribution serves your S3 bucket!")
                print(f"  >>> Use this Distribution ID in the app: {dist_id}")

        print("\n" + "=" * 60)
        print("\nNEXT STEPS:")
        print("1. Identify the correct distribution from the list above")
        print("2. Copy its Distribution ID")
        print("3. Open Cloud Stack Generator app")
        print("4. Go to Cloud Deployment tab")
        print("5. Paste the Distribution ID in the 'Distribution ID' field")
        print("6. Deploy again")

        return True

    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("CloudFront Distribution Finder")
    print("Using Cloud Stack Generator app credentials")
    print("")

    success = list_distributions()
    sys.exit(0 if success else 1)
