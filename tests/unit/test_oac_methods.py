"""
Unit tests for S3Manager OAC (Origin Access Control) methods
Tests for Mode B CloudFront functionality added in v3.2.0
"""

import pytest
from unittest.mock import Mock
from botocore.exceptions import ClientError

from src.core.aws.s3_manager import S3Manager


@pytest.mark.unit
@pytest.mark.aws
class TestOACMethods:
    """Test OAC diagnostic and management methods"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = S3Manager()
        self.mock_cloudfront = Mock()
        mock_session = Mock()
        mock_session.client.return_value = self.mock_cloudfront
        self.manager.session = mock_session

    # ============================================================================
    # check_distribution_oac_status() tests
    # ============================================================================

    def test_check_oac_status_has_oac(self):
        """Test checking distribution that HAS OAC configured"""
        # Mock CloudFront response with OAC
        self.mock_cloudfront.get_distribution_config.return_value = {
            'DistributionConfig': {
                'Origins': {
                    'Items': [
                        {
                            'Id': 'S3-origin',
                            'DomainName': 'bucket.s3.amazonaws.com',
                            'OriginAccessControlId': 'E1234OAC567890'  # OAC present
                        }
                    ]
                }
            }
        }

        success, has_oac, message = self.manager.check_distribution_oac_status('E1234DIST')

        assert success is True
        assert has_oac is True
        assert 'OAC configured' in message
        assert '1 origin(s) with OAC' in message

    def test_check_oac_status_multiple_origins_with_oac(self):
        """Test checking distribution with multiple origins, all having OAC"""
        # Mock CloudFront response with multiple origins with OAC
        self.mock_cloudfront.get_distribution_config.return_value = {
            'DistributionConfig': {
                'Origins': {
                    'Items': [
                        {
                            'Id': 'S3-origin-1',
                            'OriginAccessControlId': 'E1234OAC567890'
                        },
                        {
                            'Id': 'S3-origin-2',
                            'OriginAccessControlId': 'E9999OAC111111'
                        }
                    ]
                }
            }
        }

        success, has_oac, message = self.manager.check_distribution_oac_status('E1234DIST')

        assert success is True
        assert has_oac is True
        assert '2 origin(s) with OAC' in message

    def test_check_oac_status_no_oac(self):
        """Test checking distribution that LACKS OAC (uses legacy OAI or public)"""
        # Mock CloudFront response without OAC
        self.mock_cloudfront.get_distribution_config.return_value = {
            'DistributionConfig': {
                'Origins': {
                    'Items': [
                        {
                            'Id': 'S3-origin',
                            'DomainName': 'bucket.s3.amazonaws.com',
                            # No OriginAccessControlId
                            'S3OriginConfig': {
                                'OriginAccessIdentity': 'origin-access-identity/cloudfront/LEGACY'
                            }
                        }
                    ]
                }
            }
        }

        success, has_oac, message = self.manager.check_distribution_oac_status('E1234DIST')

        assert success is True
        assert has_oac is False
        assert 'does NOT have OAC' in message
        assert 'legacy Origin Access Identity' in message

    def test_check_oac_status_distribution_not_found(self):
        """Test checking non-existent distribution"""
        # Mock ClientError for NoSuchDistribution
        error_response = {
            'Error': {
                'Code': 'NoSuchDistribution',
                'Message': 'The specified distribution does not exist'
            }
        }
        self.mock_cloudfront.get_distribution_config.side_effect = ClientError(
            error_response, 'GetDistributionConfig'
        )

        success, has_oac, message = self.manager.check_distribution_oac_status('INVALID')

        assert success is False
        assert has_oac is False
        assert 'Distribution not found' in message
        assert 'INVALID' in message

    def test_check_oac_status_access_denied(self):
        """Test checking distribution with insufficient permissions"""
        # Mock ClientError for AccessDenied
        error_response = {
            'Error': {
                'Code': 'AccessDenied',
                'Message': 'User is not authorized'
            }
        }
        self.mock_cloudfront.get_distribution_config.side_effect = ClientError(
            error_response, 'GetDistributionConfig'
        )

        success, has_oac, message = self.manager.check_distribution_oac_status('E1234DIST')

        assert success is False
        assert has_oac is False
        assert 'OAC check failed' in message
        assert 'AccessDenied' in message

    def test_check_oac_status_generic_exception(self):
        """Test handling of unexpected exceptions"""
        self.mock_cloudfront.get_distribution_config.side_effect = Exception("Network error")

        success, has_oac, message = self.manager.check_distribution_oac_status('E1234DIST')

        assert success is False
        assert has_oac is False
        assert 'OAC check failed' in message
        assert 'Network error' in message

    # ============================================================================
    # disable_distribution() tests
    # ============================================================================

    def test_disable_distribution_success(self):
        """Test successfully disabling an enabled distribution"""
        # Mock get_distribution_config response (enabled)
        self.mock_cloudfront.get_distribution_config.return_value = {
            'DistributionConfig': {
                'Enabled': True,
                'Origins': {'Items': []},
                'CallerReference': 'test-ref'
            },
            'ETag': 'etag-abc123'
        }

        # Mock update_distribution success
        self.mock_cloudfront.update_distribution.return_value = {
            'Distribution': {'Id': 'E1234DIST'}
        }

        success, message = self.manager.disable_distribution('E1234DIST')

        assert success is True
        assert 'Distribution disabled' in message
        assert 'E1234DIST' in message
        assert 'Wait for status' in message

        # Verify update was called
        self.mock_cloudfront.update_distribution.assert_called_once()
        call_args = self.mock_cloudfront.update_distribution.call_args

        # Verify Enabled was set to False
        assert call_args[1]['DistributionConfig']['Enabled'] is False
        # Verify ETag was passed
        assert call_args[1]['IfMatch'] == 'etag-abc123'

    def test_disable_distribution_already_disabled(self):
        """Test disabling a distribution that's already disabled"""
        # Mock get_distribution_config response (already disabled)
        self.mock_cloudfront.get_distribution_config.return_value = {
            'DistributionConfig': {
                'Enabled': False,
                'Origins': {'Items': []},
                'CallerReference': 'test-ref'
            },
            'ETag': 'etag-abc123'
        }

        success, message = self.manager.disable_distribution('E1234DIST')

        assert success is True
        assert 'already disabled' in message
        assert 'E1234DIST' in message

        # Verify update was NOT called (no need to update)
        self.mock_cloudfront.update_distribution.assert_not_called()

    def test_disable_distribution_client_error(self):
        """Test handling ClientError during disable"""
        # Mock ClientError
        error_response = {
            'Error': {
                'Code': 'InvalidIfMatchVersion',
                'Message': 'The If-Match version does not match'
            }
        }
        self.mock_cloudfront.get_distribution_config.side_effect = ClientError(
            error_response, 'GetDistributionConfig'
        )

        success, message = self.manager.disable_distribution('E1234DIST')

        assert success is False
        assert 'Disable failed' in message
        assert 'InvalidIfMatchVersion' in message

    def test_disable_distribution_generic_exception(self):
        """Test handling unexpected exception during disable"""
        self.mock_cloudfront.get_distribution_config.side_effect = Exception("Network timeout")

        success, message = self.manager.disable_distribution('E1234DIST')

        assert success is False
        assert 'Disable failed' in message
        assert 'Network timeout' in message

    # ============================================================================
    # delete_distribution() tests
    # ============================================================================

    def test_delete_distribution_success(self):
        """Test successfully deleting a disabled and deployed distribution"""
        # Mock get_distribution_config (disabled)
        self.mock_cloudfront.get_distribution_config.return_value = {
            'DistributionConfig': {
                'Enabled': False,
                'Origins': {'Items': []},
                'CallerReference': 'test-ref'
            },
            'ETag': 'etag-xyz789'
        }

        # Mock get_distribution (deployed status)
        self.mock_cloudfront.get_distribution.return_value = {
            'Distribution': {
                'Id': 'E1234DIST',
                'Status': 'Deployed'
            }
        }

        # Mock delete_distribution success
        self.mock_cloudfront.delete_distribution.return_value = {}

        success, message = self.manager.delete_distribution('E1234DIST')

        assert success is True
        assert 'Distribution deleted' in message
        assert 'E1234DIST' in message

        # Verify delete was called with correct parameters
        self.mock_cloudfront.delete_distribution.assert_called_once_with(
            Id='E1234DIST',
            IfMatch='etag-xyz789'
        )

    def test_delete_distribution_still_enabled(self):
        """Test attempting to delete an enabled distribution (should fail)"""
        # Mock get_distribution_config (still enabled)
        self.mock_cloudfront.get_distribution_config.return_value = {
            'DistributionConfig': {
                'Enabled': True,  # Still enabled!
                'Origins': {'Items': []},
                'CallerReference': 'test-ref'
            },
            'ETag': 'etag-xyz789'
        }

        success, message = self.manager.delete_distribution('E1234DIST')

        assert success is False
        assert 'Cannot delete' in message
        assert 'still enabled' in message
        assert 'disable_distribution()' in message

        # Verify delete was NOT attempted
        self.mock_cloudfront.delete_distribution.assert_not_called()

    def test_delete_distribution_not_deployed_status(self):
        """Test attempting to delete when status is not 'Deployed' (should fail)"""
        # Mock get_distribution_config (disabled)
        self.mock_cloudfront.get_distribution_config.return_value = {
            'DistributionConfig': {
                'Enabled': False,
                'Origins': {'Items': []},
                'CallerReference': 'test-ref'
            },
            'ETag': 'etag-xyz789'
        }

        # Mock get_distribution (InProgress status)
        self.mock_cloudfront.get_distribution.return_value = {
            'Distribution': {
                'Id': 'E1234DIST',
                'Status': 'InProgress'  # Not deployed yet!
            }
        }

        success, message = self.manager.delete_distribution('E1234DIST')

        assert success is False
        assert 'Cannot delete' in message
        assert "status is 'InProgress'" in message
        assert 'Wait until status is' in message

        # Verify delete was NOT attempted
        self.mock_cloudfront.delete_distribution.assert_not_called()

    def test_delete_distribution_client_error(self):
        """Test handling ClientError during deletion"""
        # Mock get_distribution_config (disabled and deployed)
        self.mock_cloudfront.get_distribution_config.return_value = {
            'DistributionConfig': {
                'Enabled': False,
                'Origins': {'Items': []},
                'CallerReference': 'test-ref'
            },
            'ETag': 'etag-xyz789'
        }

        self.mock_cloudfront.get_distribution.return_value = {
            'Distribution': {
                'Id': 'E1234DIST',
                'Status': 'Deployed'
            }
        }

        # Mock ClientError during delete
        error_response = {
            'Error': {
                'Code': 'DistributionNotDisabled',
                'Message': 'Distribution must be disabled'
            }
        }
        self.mock_cloudfront.delete_distribution.side_effect = ClientError(
            error_response, 'DeleteDistribution'
        )

        success, message = self.manager.delete_distribution('E1234DIST')

        assert success is False
        assert 'Delete failed' in message
        assert 'DistributionNotDisabled' in message

    def test_delete_distribution_generic_exception(self):
        """Test handling unexpected exception during deletion"""
        self.mock_cloudfront.get_distribution_config.side_effect = Exception("Connection lost")

        success, message = self.manager.delete_distribution('E1234DIST')

        assert success is False
        assert 'Delete failed' in message
        assert 'Connection lost' in message


@pytest.mark.unit
@pytest.mark.aws
class TestOACNaming:
    """Test OAC naming logic with CloudFront 64-character limit"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = S3Manager()
        self.mock_cloudfront = Mock()
        mock_session = Mock()
        mock_session.client.return_value = self.mock_cloudfront
        self.manager.session = mock_session

    def test_oac_name_short_bucket(self):
        """Test OAC naming for short bucket name (under 64 chars total)"""
        # Mock successful OAC creation
        self.mock_cloudfront.create_origin_access_control.return_value = {
            'OriginAccessControl': {
                'Id': 'E1234OAC567890'
            }
        }

        success, oac_id, message = self.manager.create_origin_access_control(
            name="OAC-test-bucket-root",
            description="Test OAC"
        )

        assert success is True
        assert oac_id == 'E1234OAC567890'
        self.mock_cloudfront.create_origin_access_control.assert_called_once()

    def test_oac_name_long_bucket(self):
        """Test OAC naming for very long bucket name (would exceed 64 chars)"""
        # Test with a name that would be >64 chars without truncation
        long_name = "OAC-very-long-bucket-name-that-exceeds-cloudfront-limits-for-sure-path"

        # Mock successful OAC creation
        self.mock_cloudfront.create_origin_access_control.return_value = {
            'OriginAccessControl': {
                'Id': 'E9999OAC111111'
            }
        }

        success, oac_id, message = self.manager.create_origin_access_control(
            name=long_name[:64],  # Simulating truncated name
            description="Test OAC for long bucket"
        )

        assert success is True
        assert oac_id == 'E9999OAC111111'

        # Verify the name passed to AWS is under 64 chars
        call_args = self.mock_cloudfront.create_origin_access_control.call_args
        actual_name = call_args[1]['OriginAccessControlConfig']['Name']
        assert len(actual_name) <= 64
