"""
Add OAC permissions to IAM user for Mode B implementation

This script adds the required CloudFront OAC and S3 bucket policy permissions
to your IAM user so the app can auto-create CloudFront distributions.
"""
import sys
import json
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.aws.credentials import AWSCredentialsManager
from botocore.exceptions import ClientError


# Policy to add
OAC_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "CloudFrontOACPermissions",
            "Effect": "Allow",
            "Action": [
                "cloudfront:CreateOriginAccessControl",
                "cloudfront:GetOriginAccessControl",
                "cloudfront:ListOriginAccessControls",
                "cloudfront:UpdateOriginAccessControl",
                "cloudfront:CreateDistribution",
                "cloudfront:UpdateDistribution",
                "cloudfront:CreateInvalidation"
            ],
            "Resource": "*"
        },
        {
            "Sid": "S3BucketPolicyAndPublicAccess",
            "Effect": "Allow",
            "Action": [
                "s3:PutBucketPolicy",
                "s3:PutBucketPublicAccessBlock",
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::*",
                "arn:aws:s3:::*/*"
            ]
        }
    ]
}

POLICY_NAME = "CloudStackGeneratorOACPolicy"


def get_current_user(iam_client):
    """Get current IAM user name"""
    try:
        # Try to get user info from STS
        iam_client._client_config.__dict__.get('_user_provided_options', {})

        # Get caller identity to find username
        response = iam_client.meta.client.get_caller_identity()
        arn = response['Arn']

        # Extract username from ARN: arn:aws:iam::ACCOUNT:user/USERNAME
        if ':user/' in arn:
            username = arn.split(':user/')[-1]
            return username
        else:
            print("ERROR: Could not determine IAM user name from ARN:", arn)
            print("This script must be run with IAM user credentials, not assumed role.")
            return None

    except Exception as e:
        print(f"ERROR: Failed to get current user: {e}")
        return None


def check_policy_exists(iam, username: str) -> bool:
    """Check if policy already exists"""
    try:
        iam.get_user_policy(
            UserName=username,
            PolicyName=POLICY_NAME
        )
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            return False
        raise


def add_policy(iam, username: str) -> bool:
    """Add the OAC policy to the user"""
    try:
        print(f"\nAdding policy '{POLICY_NAME}' to user '{username}'...")

        iam.put_user_policy(
            UserName=username,
            PolicyName=POLICY_NAME,
            PolicyDocument=json.dumps(OAC_POLICY, indent=2)
        )

        print("[OK] Policy added successfully!")
        return True

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        print(f"\n[FAIL] Failed to add policy ({error_code})")
        print(f"Error: {e}")

        if error_code == 'AccessDenied':
            print("\nYou don't have permission to add IAM policies.")
            print("Please ask your AWS administrator to add this policy manually.")
            print("\nPolicy JSON:")
            print(json.dumps(OAC_POLICY, indent=2))

        return False


def main():
    """Main workflow"""
    print("=" * 60)
    print("Add OAC Permissions to IAM User")
    print("=" * 60)

    try:
        # Get credentials
        creds_manager = AWSCredentialsManager()

        if not creds_manager.profiles:
            print("\nERROR: No AWS profiles configured")
            return 1

        profile_name = creds_manager.active_profile or list(creds_manager.profiles.keys())[0]
        print(f"\nUsing profile: {profile_name}")

        session = creds_manager._get_session(profile_name)

        # Get STS info
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        account_id = identity['Account']
        arn = identity['Arn']

        print(f"Account ID: {account_id}")
        print(f"ARN: {arn}")

        # Extract username from ARN
        if ':user/' not in arn:
            print("\n[ERROR] This script must be run with IAM user credentials.")
            print("Your ARN indicates you're using a role, not a user.")
            print("\nPlease:")
            print("1. Use IAM user credentials (not assumed role)")
            print("2. OR ask your AWS admin to add the policy manually")
            print("\nPolicy to add:")
            print(json.dumps(OAC_POLICY, indent=2))
            return 1

        username = arn.split(':user/')[-1]
        print(f"IAM User: {username}")

        # Get IAM client
        iam = session.client('iam')

        # Check if policy already exists
        print(f"\nChecking if policy '{POLICY_NAME}' already exists...")

        if check_policy_exists(iam, username):
            print(f"[OK] Policy '{POLICY_NAME}' already exists!")
            print("\nNo action needed. Run the permission test to verify:")
            print("  python scripts/test_cloudfront_permissions.py")
            return 0

        print("[INFO] Policy does not exist yet")

        # Show what will be added
        print("\n" + "=" * 60)
        print("POLICY TO BE ADDED")
        print("=" * 60)
        print(json.dumps(OAC_POLICY, indent=2))
        print("=" * 60)

        # Confirm
        print(f"\nThis will add the inline policy '{POLICY_NAME}'")
        print(f"to IAM user: {username}")
        print(f"in account: {account_id}")
        print("\nPermissions that will be granted:")
        print("  - CloudFront: Create/manage OAC and distributions")
        print("  - S3: Update bucket policies and public access settings")
        print("  - S3: Upload objects")

        response = input("\nProceed? (yes/no): ").strip().lower()

        if response != 'yes':
            print("\nCancelled. No changes made.")
            return 0

        # Add the policy
        if add_policy(iam, username):
            print("\n" + "=" * 60)
            print("SUCCESS")
            print("=" * 60)
            print(f"\n[OK] Policy '{POLICY_NAME}' added to user '{username}'")
            print("\nNext steps:")
            print("1. Run the permission test to verify:")
            print("   python scripts/test_cloudfront_permissions.py")
            print("\n2. If test passes, Mode B implementation can proceed!")
            return 0
        else:
            return 1

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        print(f"\nERROR: AWS API call failed ({error_code})")
        print(f"Details: {e}")

        if error_code == 'AccessDenied':
            print("\nYou don't have permission to:")
            print("  - Get caller identity")
            print("  - OR manage IAM policies")
            print("\nPlease ask your AWS administrator to add the policy manually.")
            print("\nPolicy JSON:")
            print(json.dumps(OAC_POLICY, indent=2))

        return 1

    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
