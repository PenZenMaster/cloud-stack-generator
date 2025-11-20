"""
Script to check CloudFront distribution configuration
Helps diagnose origin path issues for Issue #12
"""
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.aws.s3_manager import S3Manager
import boto3


def check_distribution_config(distribution_id: str, profile_name: str = "default"):
    """
    Check CloudFront distribution origin path configuration

    Args:
        distribution_id: CloudFront distribution ID
        profile_name: AWS profile name
    """
    try:
        # Create boto3 session with profile
        try:
            session = boto3.Session(profile_name=profile_name)
        except Exception:
            print(f"ERROR: Failed to load AWS profile '{profile_name}'", file=sys.stderr)
            print("\nAvailable profiles:", file=sys.stderr)
            available_profiles = boto3.Session().available_profiles
            for p in available_profiles:
                print(f"  - {p}", file=sys.stderr)
            print(f"\nUsage: python {sys.argv[0]} <distribution_id> [profile_name]", file=sys.stderr)
            return False

        # Initialize S3Manager with session
        manager = S3Manager(session=session)
        cloudfront = manager.session.client('cloudfront')

        print(f"Checking CloudFront distribution: {distribution_id}")
        print(f"Using AWS profile: {profile_name}")
        print("-" * 60)

        # Get distribution config
        response = cloudfront.get_distribution_config(Id=distribution_id)
        config = response['DistributionConfig']

        # Display origin information
        print(f"\nOrigin Count: {config['Origins']['Quantity']}")
        print("\nOrigin Details:")

        for idx, origin in enumerate(config['Origins']['Items']):
            print(f"\n  Origin {idx}:")
            print(f"    ID: {origin['Id']}")
            print(f"    Domain: {origin['DomainName']}")
            print(f"    Origin Path: '{origin.get('OriginPath', '')}'")

            if 'S3OriginConfig' in origin:
                print("    Type: S3")
                print(f"    OAI: {origin['S3OriginConfig'].get('OriginAccessIdentity', 'None')}")

        # Display default root object
        default_root = config.get('DefaultRootObject', '')
        print(f"\nDefault Root Object: '{default_root}'")

        # Display distribution status
        dist_response = cloudfront.get_distribution(Id=distribution_id)
        status = dist_response['Distribution']['Status']
        print(f"\nDistribution Status: {status}")

        # Determine expected behavior
        origin_path = config['Origins']['Items'][0].get('OriginPath', '')
        print("\n" + "=" * 60)
        print("DIAGNOSIS:")
        print("=" * 60)

        if not origin_path:
            print("Origin Path is EMPTY (root)")
            print(f"CloudFront URL will serve: https://[domain]/{default_root or 'index.html'}")
            print(f"Maps to S3 key: {default_root or 'index.html'}")
        else:
            print(f"Origin Path is: {origin_path}")
            print(f"CloudFront URL will serve: https://[domain]/{default_root or 'index.html'}")
            print(f"Maps to S3 key: {origin_path.lstrip('/')}/{default_root or 'index.html'}")

        if status != "Deployed":
            print(f"\nWARNING: Distribution status is '{status}' not 'Deployed'")
            print("Changes may still be propagating (can take 2-15 minutes)")

        return True

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_cloudfront_config.py <distribution_id> [profile_name]")
        print("\nExample:")
        print("  python check_cloudfront_config.py E1234DISTRIBUTION")
        print("  python check_cloudfront_config.py E1234DISTRIBUTION awg-cloud-stack")
        sys.exit(1)

    dist_id = sys.argv[1]
    profile = sys.argv[2] if len(sys.argv) > 2 else "default"

    success = check_distribution_config(dist_id, profile)
    sys.exit(0 if success else 1)
