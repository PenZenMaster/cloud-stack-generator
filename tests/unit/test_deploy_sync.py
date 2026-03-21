"""
Module/Script Name: Test Deploy Sync
Path: tests/unit/test_deploy_sync.py

Description:
Unit tests for the sync_to_s3() function in s3_deployer.py.
Covers upload-only, delete-sync, dry-run, CloudFront invalidation,
and error-handling scenarios using mocked boto3 calls.

Author(s):
Rank Rocket Co (C) Copyright 2026 - All Rights Reserved

Created Date:
2026-02-18

Last Modified Date:
2026-02-18

Comments:
* v1.00 - Initial test suite for BACK-007 CLI deploy command
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, call
from botocore.exceptions import ClientError

from src.core.deployment.s3_deployer import sync_to_s3
from src.core.config.models import CloudConfig


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_cloud_config(**overrides) -> CloudConfig:
    """Return a CloudConfig populated with safe test defaults."""
    defaults = dict(
        aws_profile="test-profile",
        aws_region="us-east-1",
        bucket_name="test-bucket",
        distribution_id="EDIST123",
        auto_invalidate_cache=True,
        html_cache_control="max-age=300,public",
        asset_cache_control="max-age=86400,public",
    )
    defaults.update(overrides)
    return CloudConfig(**defaults)


def _make_session(s3_pages=None, cf_invalidation_id="INV-001"):
    """
    Build a mock boto3 Session whose client() factory returns
    appropriate mocks for 's3' and 'cloudfront'.

    Args:
        s3_pages: List of page dicts returned by the S3 paginator.
            Each page may contain a 'Contents' list of {'Key': str} dicts.
            Defaults to a single empty page (empty bucket).
        cf_invalidation_id: ID returned by create_invalidation.

    Returns:
        Tuple of (session_mock, s3_client_mock, cf_client_mock).
    """
    if s3_pages is None:
        s3_pages = [{}]  # empty bucket - no Contents key

    session = MagicMock()

    # S3 client
    s3 = MagicMock()
    paginator = MagicMock()
    paginator.paginate.return_value = iter(s3_pages)
    s3.get_paginator.return_value = paginator

    # CloudFront client
    cf = MagicMock()
    cf.create_invalidation.return_value = {
        "Invalidation": {"Id": cf_invalidation_id}
    }

    def _client_factory(service_name, **kwargs):
        if service_name == "s3":
            return s3
        if service_name == "cloudfront":
            return cf
        return MagicMock()

    session.client.side_effect = _client_factory
    return session, s3, cf


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestSyncToS3UploadOnly:
    """Files are uploaded when the bucket is empty."""

    def test_all_local_files_uploaded(self, tmp_path):
        (tmp_path / "index.html").write_text("<html></html>")
        (tmp_path / "style.css").write_text("body {}")

        session, s3, cf = _make_session(s3_pages=[{}])
        cloud = _make_cloud_config(distribution_id="", auto_invalidate_cache=False)

        result = sync_to_s3(tmp_path, "test-bucket", session, cloud)

        assert result["success"] is True
        assert result["files_uploaded"] == 2
        assert result["files_deleted"] == 0
        assert result["errors"] == []
        assert s3.put_object.call_count == 2
        assert s3.delete_objects.call_count == 0

    def test_html_gets_html_cache_control(self, tmp_path):
        (tmp_path / "page.html").write_text("<html></html>")

        session, s3, cf = _make_session()
        cloud = _make_cloud_config(
            auto_invalidate_cache=False,
            distribution_id="",
            html_cache_control="max-age=300,public",
            asset_cache_control="max-age=86400,public",
        )

        sync_to_s3(tmp_path, "test-bucket", session, cloud)

        _, kwargs = s3.put_object.call_args
        assert kwargs["CacheControl"] == "max-age=300,public"
        assert kwargs["ContentType"] == "text/html"

    def test_css_gets_asset_cache_control(self, tmp_path):
        (tmp_path / "app.css").write_text("body {}")

        session, s3, cf = _make_session()
        cloud = _make_cloud_config(
            auto_invalidate_cache=False,
            distribution_id="",
            html_cache_control="max-age=300,public",
            asset_cache_control="max-age=86400,public",
        )

        sync_to_s3(tmp_path, "test-bucket", session, cloud)

        _, kwargs = s3.put_object.call_args
        assert kwargs["CacheControl"] == "max-age=86400,public"
        assert kwargs["ContentType"] == "text/css"

    def test_s3_keys_use_forward_slashes(self, tmp_path):
        subdir = tmp_path / "cities"
        subdir.mkdir()
        (subdir / "miami.html").write_text("<html></html>")

        session, s3, _ = _make_session()
        cloud = _make_cloud_config(auto_invalidate_cache=False, distribution_id="")

        sync_to_s3(tmp_path, "test-bucket", session, cloud)

        _, kwargs = s3.put_object.call_args
        assert "\\" not in kwargs["Key"]
        assert "cities/miami.html" == kwargs["Key"]


class TestSyncToS3DeleteSync:
    """Orphaned S3 objects are deleted when not present locally."""

    def test_orphaned_objects_deleted(self, tmp_path):
        (tmp_path / "index.html").write_text("<html></html>")

        # S3 has an extra file that no longer exists locally
        s3_pages = [{"Contents": [
            {"Key": "index.html"},
            {"Key": "old-page.html"},
        ]}]
        session, s3, _ = _make_session(s3_pages=s3_pages)
        cloud = _make_cloud_config(auto_invalidate_cache=False, distribution_id="")

        result = sync_to_s3(tmp_path, "test-bucket", session, cloud)

        assert result["success"] is True
        assert result["files_uploaded"] == 1  # index.html
        assert result["files_deleted"] == 1   # old-page.html
        s3.delete_objects.assert_called_once()
        delete_call_kwargs = s3.delete_objects.call_args[1]
        deleted_keys = [o["Key"] for o in delete_call_kwargs["Delete"]["Objects"]]
        assert "old-page.html" in deleted_keys

    def test_delete_batch_quiet_mode(self, tmp_path):
        """delete_objects is called with Quiet=True."""
        s3_pages = [{"Contents": [{"Key": "stale.html"}]}]
        session, s3, _ = _make_session(s3_pages=s3_pages)
        cloud = _make_cloud_config(auto_invalidate_cache=False, distribution_id="")

        sync_to_s3(tmp_path, "test-bucket", session, cloud)

        s3.delete_objects.assert_called_once()
        kwargs = s3.delete_objects.call_args[1]
        assert kwargs["Delete"]["Quiet"] is True


class TestSyncToS3DryRun:
    """Dry-run returns a plan without making any API mutations."""

    def test_dry_run_returns_plan_no_api_calls(self, tmp_path):
        (tmp_path / "index.html").write_text("<html></html>")
        (tmp_path / "app.css").write_text("body {}")

        s3_pages = [{"Contents": [{"Key": "old.html"}]}]
        session, s3, cf = _make_session(s3_pages=s3_pages)
        cloud = _make_cloud_config()

        result = sync_to_s3(tmp_path, "test-bucket", session, cloud, dry_run=True)

        assert result["success"] is True
        assert "plan" in result
        plan = result["plan"]
        assert plan["total_upload"] == 2
        assert plan["total_delete"] == 1
        assert "old.html" in plan["files_to_delete"]
        # No mutations
        s3.put_object.assert_not_called()
        s3.delete_objects.assert_not_called()
        cf.create_invalidation.assert_not_called()

    def test_dry_run_upload_list_sorted(self, tmp_path):
        (tmp_path / "z.html").write_text("z")
        (tmp_path / "a.html").write_text("a")

        session, s3, _ = _make_session()
        cloud = _make_cloud_config()

        result = sync_to_s3(tmp_path, "test-bucket", session, cloud, dry_run=True)

        plan = result["plan"]
        assert plan["files_to_upload"] == sorted(plan["files_to_upload"])


class TestSyncToS3CloudFrontInvalidation:
    """CloudFront invalidation is triggered or skipped based on config."""

    def test_invalidation_triggered_when_configured(self, tmp_path):
        (tmp_path / "index.html").write_text("<html></html>")

        session, s3, cf = _make_session(cf_invalidation_id="INV-TEST-99")
        cloud = _make_cloud_config(
            distribution_id="EDIST456",
            auto_invalidate_cache=True,
        )

        result = sync_to_s3(tmp_path, "test-bucket", session, cloud)

        assert result["invalidation_id"] == "INV-TEST-99"
        cf.create_invalidation.assert_called_once()
        inv_call = cf.create_invalidation.call_args[1]
        assert inv_call["DistributionId"] == "EDIST456"
        assert inv_call["InvalidationBatch"]["Paths"]["Items"] == ["/*"]

    def test_invalidation_skipped_when_disabled(self, tmp_path):
        (tmp_path / "index.html").write_text("<html></html>")

        session, s3, cf = _make_session()
        cloud = _make_cloud_config(
            distribution_id="EDIST456",
            auto_invalidate_cache=False,
        )

        result = sync_to_s3(tmp_path, "test-bucket", session, cloud)

        assert result["invalidation_id"] is None
        cf.create_invalidation.assert_not_called()

    def test_invalidation_skipped_when_no_distribution_id(self, tmp_path):
        (tmp_path / "index.html").write_text("<html></html>")

        session, s3, cf = _make_session()
        cloud = _make_cloud_config(
            distribution_id="",
            auto_invalidate_cache=True,
        )

        result = sync_to_s3(tmp_path, "test-bucket", session, cloud)

        assert result["invalidation_id"] is None
        cf.create_invalidation.assert_not_called()


class TestSyncToS3ErrorHandling:
    """Errors are captured without halting the entire sync."""

    def test_upload_client_error_recorded_in_errors(self, tmp_path):
        (tmp_path / "good.html").write_text("<html>good</html>")
        (tmp_path / "bad.html").write_text("<html>bad</html>")

        session, s3, cf = _make_session()
        cloud = _make_cloud_config(auto_invalidate_cache=False, distribution_id="")

        # Fail for bad.html only
        def _put_object_side_effect(**kwargs):
            if kwargs.get("Key") == "bad.html":
                error_response = {"Error": {"Code": "AccessDenied", "Message": "Denied"}}
                raise ClientError(error_response, "PutObject")

        s3.put_object.side_effect = _put_object_side_effect

        result = sync_to_s3(tmp_path, "test-bucket", session, cloud)

        assert result["success"] is False
        assert result["files_uploaded"] == 1  # good.html succeeded
        assert len(result["errors"]) == 1
        assert "bad.html" in result["errors"][0]

    def test_list_objects_error_returns_failure(self, tmp_path):
        (tmp_path / "index.html").write_text("<html></html>")

        session = MagicMock()
        s3 = MagicMock()
        paginator = MagicMock()
        error_response = {"Error": {"Code": "NoSuchBucket", "Message": "Not found"}}
        paginator.paginate.return_value = iter([])
        # Raise on iteration
        paginator.paginate.side_effect = ClientError(error_response, "ListObjectsV2")
        s3.get_paginator.return_value = paginator
        session.client.return_value = s3

        cloud = _make_cloud_config(auto_invalidate_cache=False, distribution_id="")

        result = sync_to_s3(tmp_path, "test-bucket", session, cloud)

        assert result["success"] is False
        assert result["files_uploaded"] == 0
        assert any("NoSuchBucket" in e or "test-bucket" in e for e in result["errors"])

    def test_progress_callback_called(self, tmp_path):
        (tmp_path / "index.html").write_text("<html></html>")

        session, s3, _ = _make_session()
        cloud = _make_cloud_config(auto_invalidate_cache=False, distribution_id="")
        messages = []

        sync_to_s3(tmp_path, "test-bucket", session, cloud, progress_callback=messages.append)

        assert any("index.html" in m for m in messages)
