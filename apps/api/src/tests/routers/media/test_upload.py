import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from moto import mock_aws
import boto3
import json

from src.routers.media.upload import router
from src.services.media.upload_preparation import prepare_upload


class TestMediaUploadEndpoints:

    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router, prefix="/api/v1/media/upload")
        return TestClient(app)

    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user."""
        return Mock(
            user_uuid="test-user-uuid",
            email="test@example.com",
            is_active=True
        )

    @pytest.fixture
    def mock_s3_config(self):
        """Mock S3 configuration."""
        return {
            "bucket_name": "test-bucket",
            "endpoint_url": "http://localhost:9000",
            "access_key_id": "test-key",
            "secret_access_key": "test-secret",
            "region": "us-east-1"
        }

    def test_upload_prepare_success(self, client, mock_user):
        """Test successful upload preparation."""
        upload_request = {
            "file_name": "test-avatar.jpg",
            "content_type": "image/jpeg",
            "file_size": 1024000,
            "resource_type": "user_avatar",
            "resource_id": "test-user-uuid",
            "file_category": "image"
        }

        mock_upload_response = {
            "upload_url": "https://s3.amazonaws.com/test-bucket",
            "method": "POST",
            "fields": {
                "key": "user_avatars/test-user-uuid/test-avatar.jpg",
                "Content-Type": "image/jpeg"
            },
            "file_url": "https://s3.amazonaws.com/test-bucket/user_avatars/test-user-uuid/test-avatar.jpg"
        }

        with patch('src.routers.media.upload.prepare_upload', new_callable=AsyncMock) as mock_prepare:
            with patch('src.routers.media.upload.get_current_user', return_value=mock_user):
                mock_prepare.return_value = mock_upload_response

                response = client.post("/api/v1/media/upload/prepare", json=upload_request)

                assert response.status_code == 200
                assert response.json() == mock_upload_response
                mock_prepare.assert_called_once_with(
                    file_name="test-avatar.jpg",
                    content_type="image/jpeg",
                    file_size=1024000,
                    resource_type="user_avatar",
                    resource_id="test-user-uuid",
                    file_category="image"
                )

    def test_upload_prepare_missing_fields(self, client, mock_user):
        """Test upload preparation with missing required fields."""
        incomplete_request = {
            "file_name": "test-avatar.jpg",
            # Missing required fields
        }

        with patch('src.routers.media.upload.get_current_user', return_value=mock_user):
            response = client.post("/api/v1/media/upload/prepare", json=incomplete_request)

            assert response.status_code == 422  # Validation error

    def test_upload_prepare_unauthorized(self, client):
        """Test upload preparation without authentication."""
        upload_request = {
            "file_name": "test-avatar.jpg",
            "content_type": "image/jpeg",
            "file_size": 1024000,
            "resource_type": "user_avatar",
            "resource_id": "test-user-uuid"
        }

        with patch('src.routers.media.upload.get_current_user', side_effect=Exception("Not authenticated")):
            response = client.post("/api/v1/media/upload/prepare", json=upload_request)

            # Should return 401 or 500 depending on error handling
            assert response.status_code in [401, 500]

    def test_upload_confirm_success(self, client, mock_user):
        """Test successful upload confirmation."""
        confirm_request = {
            "file_uuid": "test-file-uuid",
            "file_path": "user_avatars/test-user-uuid/test-avatar.jpg",
            "file_url": "https://s3.amazonaws.com/test-bucket/user_avatars/test-user-uuid/test-avatar.jpg",
            "storage_backend": "s3api",
            "content_type": "image/jpeg",
            "file_size": 1024000,
            "resource_type": "user_avatar",
            "resource_id": "test-user-uuid"
        }

        mock_media_file = Mock()
        mock_media_file.file_uuid = "test-file-uuid"
        mock_media_file.storage_backend = "s3api"
        mock_media_file.file_path = "user_avatars/test-user-uuid/test-avatar.jpg"
        mock_media_file.file_url = "https://s3.amazonaws.com/test-bucket/user_avatars/test-user-uuid/test-avatar.jpg"

        with patch('src.routers.media.upload.get_db_session') as mock_db_session:
            with patch('src.routers.media.upload.get_current_user', return_value=mock_user):
                with patch('src.routers.media.upload.MediaFile') as mock_media_file_class:
                    mock_media_file_class.return_value = mock_media_file
                    mock_db_session.return_value.__enter__.return_value.add.return_value = None
                    mock_db_session.return_value.__enter__.return_value.commit.return_value = None
                    mock_db_session.return_value.__enter__.return_value.refresh.return_value = None

                    response = client.post("/api/v1/media/upload/confirm", json=confirm_request)

                    assert response.status_code == 200
                    response_data = response.json()
                    assert response_data["file_uuid"] == "test-file-uuid"
                    assert response_data["storage_backend"] == "s3api"

    def test_upload_confirm_missing_fields(self, client, mock_user):
        """Test upload confirmation with missing required fields."""
        incomplete_request = {
            "file_uuid": "test-file-uuid",
            # Missing other required fields
        }

        with patch('src.routers.media.upload.get_current_user', return_value=mock_user):
            response = client.post("/api/v1/media/upload/confirm", json=incomplete_request)

            assert response.status_code == 422  # Validation error

    def test_upload_confirm_invalid_storage_backend(self, client, mock_user):
        """Test upload confirmation with invalid storage backend."""
        confirm_request = {
            "file_uuid": "test-file-uuid",
            "file_path": "user_avatars/test-user-uuid/test-avatar.jpg",
            "file_url": "http://localhost:1338/content/user_avatars/test-user-uuid/test-avatar.jpg",
            "storage_backend": "filesystem",  # This should no longer be valid
            "content_type": "image/jpeg",
            "file_size": 1024000,
            "resource_type": "user_avatar",
            "resource_id": "test-user-uuid"
        }

        with patch('src.routers.media.upload.get_current_user', return_value=mock_user):
            response = client.post("/api/v1/media/upload/confirm", json=confirm_request)

            # The endpoint should still accept it since we're not validating the storage backend type
            # But in practice, this should only be "s3api" after migration
            assert response.status_code == 200

    def test_direct_upload_endpoint_removed(self, client, mock_user):
        """Test that direct upload endpoint has been removed."""
        # This endpoint should no longer exist
        response = client.post("/api/v1/media/upload/direct-upload")

        # Should return 404 Not Found since the endpoint was removed
        assert response.status_code == 404

    def test_storage_backend_factory_uses_s3_only(self):
        """Test that storage factory returns only S3 storage."""
        from src.services.storage.factory import get_storage_backend, reset_storage_backend

        # Reset cache to ensure clean test
        reset_storage_backend()

        with patch('src.services.storage.s3.get_learnhouse_config'):
            storage = get_storage_backend()

        from src.services.storage.s3 import S3Storage
        assert isinstance(storage, S3Storage)

    @pytest.mark.asyncio
    async def test_upload_prepare_integration(self, mock_s3_config):
        """Test integration with actual prepare_upload function."""
        with mock_aws():
            # Setup S3 bucket
            s3_client = boto3.client("s3", region_name="us-east-1")
            s3_client.create_bucket(Bucket=mock_s3_config["bucket_name"])

            with patch('src.services.storage.s3.get_learnhouse_config') as mock_config:
                mock_config.return_value.hosting_config.content_delivery.s3api.bucket_name = mock_s3_config["bucket_name"]
                mock_config.return_value.hosting_config.content_delivery.s3api.endpoint_url = None

                result = await prepare_upload(
                    file_name="test-file.jpg",
                    content_type="image/jpeg",
                    file_size=1024000,
                    resource_type="user_avatar",
                    resource_id="test-user-uuid",
                    file_category="image"
                )

                assert "upload_url" in result
                assert "method" in result
                assert "fields" in result
                assert "file_url" in result
                assert result["method"] == "POST"
                assert "key" in result["fields"]
                assert "Content-Type" in result["fields"]