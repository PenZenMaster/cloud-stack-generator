"""
Test CloudFront and S3 permissions for Mode B implementation

This script verifies the AWS credentials have all required permissions
for CloudFront OAC auto-creation and Mode B deployment.
"""
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.aws.credentials import AWSCredentialsManager
from botocore.exceptions import ClientError


def test_permission(client, operation: str, **kwargs) -> tuple[bool, str]:
    """
    Test if a specific AWS operation is allowed.

    Args:
        client: boto3 client
        operation: Operation name (e.g., 'list_distributions')
        **kwargs: Parameters for the operation

    Returns:
        (has_permission, message)
    """
    try:
        getattr(client, operation)(**kwargs)
        return True, "OK"
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')

        if error_code in ['AccessDenied', 'UnauthorizedOperation', 'AccessDeniedException']:
            return False, f"Access Denied ({error_code})"
        elif error_code in ['InvalidParameterValue', 'NoSuchEntity', 'NoSuchDistribution', 'NoSuchOriginAccessControl']:
            # These errors mean we have permission but the resource doesn't exist
            return True, "OK (tested)"
        else:
            return False, f"Error: {error_code}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def check_cloudfront_permissions(session) -> dict:
    """Check CloudFront permissions"""
    print("\n" + "=" * 60)
    print("CLOUDFRONT PERMISSIONS")
    print("=" * 60)

    cloudfront = session.client('cloudfront')
    results = {}

    tests = [
        ('list_distributions', {}, 'List Distributions'),
        ('list_origin_access_controls', {}, 'List OACs'),
        ('get_distribution', {'Id': 'NONEXISTENT'}, 'Get Distribution'),
        ('get_origin_access_control', {'Id': 'NONEXISTENT'}, 'Get OAC'),
    ]

    for operation, params, description in tests:
        print(f"\n{description}:")
        print(f"  Operation: cloudfront:{operation}")

        has_perm, message = test_permission(cloudfront, operation, **params)
        results[operation] = has_perm

        if has_perm:
            print(f"  Status: [OK] {message}")
        else:
            print(f"  Status: [FAIL] {message}")

    return results


def check_s3_permissions(session, test_bucket: str) -> dict:
    """Check S3 permissions"""
    print("\n" + "=" * 60)
    print("S3 PERMISSIONS")
    print("=" * 60)

    s3 = session.client('s3')
    results = {}

    # Test with a bucket name
    if not test_bucket:
        print("\nNo test bucket specified - using 'test-bucket' for permission checks")
        test_bucket = 'test-bucket'

    tests = [
        ('list_buckets', {}, 'List Buckets'),
        ('get_bucket_policy', {'Bucket': test_bucket}, 'Get Bucket Policy'),
        ('get_bucket_website', {'Bucket': test_bucket}, 'Get Bucket Website'),
        ('get_public_access_block', {'Bucket': test_bucket}, 'Get Public Access Block'),
    ]

    for operation, params, description in tests:
        print(f"\n{description}:")
        print(f"  Operation: s3:{operation}")

        has_perm, message = test_permission(s3, operation, **params)
        results[operation] = has_perm

        if has_perm:
            print(f"  Status: [OK] {message}")
        else:
            print(f"  Status: [FAIL] {message}")

    return results


def check_sts_permissions(session) -> dict:
    """Check STS permissions"""
    print("\n" + "=" * 60)
    print("STS PERMISSIONS (Account Identity)")
    print("=" * 60)

    sts = session.client('sts')
    results = {}

    print("\nGet Caller Identity:")
    print("  Operation: sts:GetCallerIdentity")

    has_perm, message = test_permission(sts, 'get_caller_identity')
    results['get_caller_identity'] = has_perm

    if has_perm:
        print(f"  Status: [OK] {message}")

        # Show account info
        try:
            identity = sts.get_caller_identity()
            print(f"\n  Account ID: {identity['Account']}")
            print(f"  User ARN: {identity['Arn']}")
        except Exception:
            pass
    else:
        print(f"  Status: [FAIL] {message}")

    return results


def analyze_results(cf_results: dict, s3_results: dict, sts_results: dict):
    """Analyze test results and provide recommendations"""
    print("\n" + "=" * 60)
    print("ANALYSIS")
    print("=" * 60)

    # Required for Mode B
    required_cf = {
        'list_distributions': 'List CloudFront distributions',
        'list_origin_access_controls': 'List OACs',
        'get_distribution': 'Get distribution config',
        'get_origin_access_control': 'Get OAC config',
    }

    required_s3 = {
        'list_buckets': 'List S3 buckets',
        'get_bucket_policy': 'Get/Set bucket policy',
        'get_bucket_website': 'Configure website hosting',
        'get_public_access_block': 'Configure public access block',
    }

    required_sts = {
        'get_caller_identity': 'Get AWS account ID',
    }

    # Check what's missing
    missing = []

    print("\nRequired CloudFront Permissions:")
    for operation, description in required_cf.items():
        has = cf_results.get(operation, False)
        status = "[OK]" if has else "[MISSING]"
        print(f"  {status} {description}")
        if not has:
            missing.append(f"cloudfront:{operation}")

    print("\nRequired S3 Permissions:")
    for operation, description in required_s3.items():
        has = s3_results.get(operation, False)
        status = "[OK]" if has else "[MISSING]"
        print(f"  {status} {description}")
        if not has:
            missing.append(f"s3:{operation}")

    print("\nRequired STS Permissions:")
    for operation, description in required_sts.items():
        has = sts_results.get(operation, False)
        status = "[OK]" if has else "[MISSING]"
        print(f"  {status} {description}")
        if not has:
            missing.append(f"sts:{operation}")

    # Additional permissions needed (can't test without creating resources)
    print("\nAdditional Permissions Needed (cannot test without creating resources):")
    additional = [
        "cloudfront:CreateOriginAccessControl",
        "cloudfront:CreateDistribution",
        "cloudfront:UpdateDistribution",
        "cloudfront:CreateInvalidation",
        "s3:PutBucketPolicy",
        "s3:PutBucketPublicAccessBlock",
        "s3:PutObject"
    ]

    for perm in additional:
        print(f"  ? {perm} (assumed needed)")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if missing:
        print("\n[FAIL] MISSING PERMISSIONS DETECTED")
        print(f"\nYou are missing {len(missing)} testable permission(s):")
        for perm in missing:
            print(f"  - {perm}")

        print("\nAction Required:")
        print("1. Review docs/OAC_PERMISSIONS_EXPLAINED.md")
        print("2. Add missing permissions to your IAM policy")
        print("3. Re-run this test to verify")

        return False
    else:
        print("\n[PASS] ALL TESTABLE PERMISSIONS OK")
        print("\nNote: Some permissions cannot be tested without creating resources.")
        print("If deployment fails, you may need to add:")
        for perm in additional:
            print(f"  - {perm}")

        print("\nRecommendation:")
        print("- Add complete IAM policy from docs/OAC_PERMISSIONS_EXPLAINED.md")
        print("- This ensures all Mode B operations will work")

        return True


def main():
    """Main test workflow"""
    print("CloudFront OAC Permissions Test")
    print("Testing AWS credentials for Mode B deployment")
    print("")

    try:
        # Get credentials
        creds_manager = AWSCredentialsManager()

        if not creds_manager.profiles:
            print("ERROR: No AWS profiles configured")
            print("\nPlease configure AWS credentials in the app first.")
            return 1

        profile_name = creds_manager.active_profile or list(creds_manager.profiles.keys())[0]
        print(f"Testing profile: {profile_name}")

        session = creds_manager._get_session(profile_name)

        # Test permissions
        cf_results = check_cloudfront_permissions(session)
        s3_results = check_s3_permissions(session, 'portable-sanitation-solutions')
        sts_results = check_sts_permissions(session)

        # Analyze
        success = analyze_results(cf_results, s3_results, sts_results)

        return 0 if success else 1

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
