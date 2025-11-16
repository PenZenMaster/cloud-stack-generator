"""
Clean up duplicate CloudFront distributions

This script helps identify and remove duplicate CloudFront distributions
to reduce AWS costs and clean up test artifacts.

SAFETY FEATURES:
- Shows what will be deleted BEFORE doing anything
- Requires explicit confirmation
- Disables distributions first (can be re-enabled if mistake)
- Waits for disable to complete before deleting
- Logs all actions
"""
import sys
from pathlib import Path
from time import sleep
from typing import List, Dict, Tuple

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.aws.credentials import AWSCredentialsManager
from botocore.exceptions import ClientError


def group_distributions_by_origin(distributions: List[Dict]) -> Dict[str, List[Dict]]:
    """Group distributions by their origin domain"""
    grouped = {}
    for dist in distributions:
        origins = dist['Origins']['Items']
        if origins:
            origin_domain = origins[0]['DomainName']
            if origin_domain not in grouped:
                grouped[origin_domain] = []
            grouped[origin_domain].append(dist)
    return grouped


def identify_duplicates(distributions: List[Dict]) -> List[str]:
    """
    Identify duplicate distributions that can be safely deleted.

    Strategy: For each origin domain, keep the OLDEST distribution
    and mark newer ones as duplicates.
    """
    grouped = group_distributions_by_origin(distributions)
    duplicates = []

    for origin_domain, dists in grouped.items():
        if len(dists) > 1:
            # Sort by ID (older IDs come first alphabetically)
            dists_sorted = sorted(dists, key=lambda d: d['Id'])

            # Keep the first one, mark rest as duplicates
            for dist in dists_sorted[1:]:
                duplicates.append(dist['Id'])

    return duplicates


def disable_distribution(cloudfront, dist_id: str) -> Tuple[bool, str]:
    """Disable a CloudFront distribution"""
    try:
        # Get current config
        response = cloudfront.get_distribution_config(Id=dist_id)
        config = response['DistributionConfig']
        etag = response['ETag']

        # Check if already disabled
        if not config['Enabled']:
            return True, "Already disabled"

        # Disable it
        config['Enabled'] = False
        cloudfront.update_distribution(
            Id=dist_id,
            DistributionConfig=config,
            IfMatch=etag
        )

        return True, "Disabled successfully"

    except ClientError as e:
        return False, f"Error: {e}"


def wait_for_deployment(cloudfront, dist_id: str, max_wait: int = 300) -> bool:
    """Wait for distribution to finish deploying (status = Deployed)"""
    print(f"  Waiting for distribution {dist_id} to deploy...", end='', flush=True)

    waited = 0
    while waited < max_wait:
        try:
            response = cloudfront.get_distribution(Id=dist_id)
            status = response['Distribution']['Status']

            if status == 'Deployed':
                print(" Done!")
                return True

            print(".", end='', flush=True)
            sleep(10)
            waited += 10

        except ClientError:
            return False

    print(" Timeout!")
    return False


def delete_distribution(cloudfront, dist_id: str) -> Tuple[bool, str]:
    """Delete a CloudFront distribution (must be disabled first)"""
    try:
        # Get current ETag
        response = cloudfront.get_distribution_config(Id=dist_id)
        etag = response['ETag']

        # Delete it
        cloudfront.delete_distribution(
            Id=dist_id,
            IfMatch=etag
        )

        return True, "Deleted successfully"

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        if error_code == 'DistributionNotDisabled':
            return False, "ERROR: Distribution must be disabled first"
        return False, f"Error: {e}"


def main():
    """Main cleanup workflow"""
    print("CloudFront Distribution Cleanup Tool")
    print("=" * 60)

    try:
        # Get credentials
        creds_manager = AWSCredentialsManager()

        if not creds_manager.profiles:
            print("ERROR: No AWS profiles configured")
            return 1

        profile_name = creds_manager.active_profile or list(creds_manager.profiles.keys())[0]
        print(f"Using profile: {profile_name}\n")

        session = creds_manager._get_session(profile_name)
        cloudfront = session.client('cloudfront')

        # List all distributions
        print("Fetching distributions...")
        response = cloudfront.list_distributions()

        if response['DistributionList']['Quantity'] == 0:
            print("No distributions found.")
            return 0

        distributions = response['DistributionList']['Items']
        print(f"Found {len(distributions)} distributions\n")

        # Identify duplicates
        duplicates = identify_duplicates(distributions)

        if not duplicates:
            print("No duplicates found. All distributions appear unique.")
            return 0

        print(f"Found {len(duplicates)} duplicate distributions:\n")

        # Show what will be cleaned up
        for dist in distributions:
            if dist['Id'] in duplicates:
                origins = dist['Origins']['Items']
                origin_domain = origins[0]['DomainName'] if origins else 'N/A'
                domain = dist['DomainName']
                comment = dist.get('Comment', 'No comment')
                enabled = "ENABLED" if dist['Enabled'] else "disabled"

                print(f"  {dist['Id']} - {domain}")
                print(f"    Origin: {origin_domain}")
                print(f"    Comment: {comment}")
                print(f"    Status: {enabled}")
                print()

        # Get confirmation
        print("=" * 60)
        print("SAFETY CHECK")
        print("=" * 60)
        print(f"This will DISABLE then DELETE {len(duplicates)} distributions.")
        print("Distributions will be disabled first (can be re-enabled if needed).")
        print("After confirming they're disabled, they will be permanently deleted.")
        print()

        confirm = input("Type 'DELETE' to proceed, or anything else to cancel: ")

        if confirm != 'DELETE':
            print("\nCancelled. No changes made.")
            return 0

        # Disable all duplicates first
        print("\n" + "=" * 60)
        print("PHASE 1: Disabling distributions")
        print("=" * 60)

        for dist_id in duplicates:
            print(f"\nDisabling {dist_id}...")
            success, message = disable_distribution(cloudfront, dist_id)
            print(f"  {message}")

            if success and message != "Already disabled":
                wait_for_deployment(cloudfront, dist_id)

        # Ask for confirmation again before deleting
        print("\n" + "=" * 60)
        print("PHASE 2: Deleting distributions")
        print("=" * 60)
        print("All duplicates have been disabled.")
        print("Ready to permanently delete them.")
        print()

        confirm2 = input("Type 'CONFIRM DELETE' to proceed with deletion: ")

        if confirm2 != 'CONFIRM DELETE':
            print("\nDeletion cancelled. Distributions remain disabled.")
            print("You can re-enable them manually in AWS Console if needed.")
            return 0

        # Delete all duplicates
        deleted_count = 0
        for dist_id in duplicates:
            print(f"\nDeleting {dist_id}...")
            success, message = delete_distribution(cloudfront, dist_id)
            print(f"  {message}")

            if success:
                deleted_count += 1

        print("\n" + "=" * 60)
        print("CLEANUP COMPLETE")
        print("=" * 60)
        print(f"Successfully deleted {deleted_count} of {len(duplicates)} distributions")
        print("\nRemaining distributions:")

        # List what's left
        response = cloudfront.list_distributions()
        if response['DistributionList']['Quantity'] > 0:
            remaining = response['DistributionList']['Items']
            grouped = group_distributions_by_origin(remaining)

            for origin, dists in grouped.items():
                print(f"\n  {origin}:")
                for dist in dists:
                    print(f"    - {dist['Id']} ({dist['DomainName']})")
        else:
            print("  None (all deleted)")

        return 0

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
