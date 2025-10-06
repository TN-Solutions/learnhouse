import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from moto import mock_aws
import boto3

# Import the migrator class
from migrate_filesystem_to_s3 import FileSystemToS3Migrator


class TestFileSystemToS3Migrator:

    @pytest.fixture
    def mock_s3_config(self):
        return {
            "bucket_name": "test-bucket",
            "endpoint_url": "http://localhost:9000",
            "access_key_id": "test-key",
            "secret_access_key": "test-secret",
            "region": "us-east-1"
        }

    @pytest.fixture
    def temp_content_dir(self):
        """Create a temporary content directory with test files."""
        temp_dir = tempfile.mkdtemp()
        content_dir = Path(temp_dir) / "content"
        content_dir.mkdir()

        # Create test directory structure
        org_dir = content_dir / "orgs" / "test-org-id" / "courses" / "test-course-id" / "activities"
        org_dir.mkdir(parents=True)

        # Create test files
        test_file1 = org_dir / "video.mp4"
        test_file2 = org_dir / "document.pdf"

        test_file1.write_bytes(b"test video content")
        test_file2.write_bytes(b"test document content")

        yield str(content_dir)

        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def mock_media_files(self):
        """Mock media file database records."""
        return [
            {
                "file_uuid": "test-uuid-1",
                "storage_backend": "filesystem",
                "file_path": "orgs/test-org-id/courses/test-course-id/activities/video.mp4",
                "file_url": "http://localhost:1338/content/orgs/test-org-id/courses/test-course-id/activities/video.mp4",
                "resource_type": "course_activity",
                "resource_id": "test-activity-id"
            },
            {
                "file_uuid": "test-uuid-2",
                "storage_backend": "s3api",
                "file_path": "orgs/test-org-id/courses/test-course-id/activities/document.pdf",
                "file_url": "https://s3.amazonaws.com/test-bucket/orgs/test-org-id/courses/test-course-id/activities/document.pdf",
                "resource_type": "course_activity",
                "resource_id": "test-activity-id-2"
            }
        ]

    @pytest.mark.asyncio
    async def test_scan_filesystem_files(self, mock_s3_config, temp_content_dir):
        """Test scanning filesystem for files."""
        migrator = FileSystemToS3Migrator(mock_s3_config)
        migrator.content_dir = Path(temp_content_dir)

        files = await migrator.scan_filesystem_files()

        assert len(files) == 2
        assert any(f["s3_key"] == "orgs/test-org-id/courses/test-course-id/activities/video.mp4" for f in files)
        assert any(f["s3_key"] == "orgs/test-org-id/courses/test-course-id/activities/document.pdf" for f in files)

    @pytest.mark.asyncio
    async def test_get_media_files_from_db(self, mock_s3_config, mock_media_files):
        """Test getting media files from database."""
        migrator = FileSystemToS3Migrator(mock_s3_config)

        with patch('migrate_filesystem_to_s3.get_db_session') as mock_db_session:
            with patch('migrate_filesystem_to_s3.MediaFile') as mock_media_file_model:
                # Setup mock query
                mock_query = Mock()
                mock_query.all.return_value = mock_media_files
                mock_db_session.return_value.__enter__.return_value.query.return_value = mock_query

                files = await migrator.get_media_files_from_db()

                assert len(files) == 2
                assert files[0]["storage_backend"] == "filesystem"
                assert files[1]["storage_backend"] == "s3api"

    @pytest.mark.asyncio
    async def test_upload_file_to_s3(self, mock_s3_config):
        """Test uploading a file to S3."""
        with mock_aws():
            # Create S3 client and bucket
            s3_client = boto3.client("s3", region_name="us-east-1")
            s3_client.create_bucket(Bucket=mock_s3_config["bucket_name"])

            # Update migrator to use real S3 client for testing
            migrator = FileSystemToS3Migrator(mock_s3_config)
            migrator.s3_client = s3_client

            # Create temporary test file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(b"test content")
                temp_file_path = temp_file.name

            try:
                result = await migrator.upload_file_to_s3(temp_file_path, "test/file.txt")
                assert result is True

                # Verify file was uploaded
                response = s3_client.head_object(
                    Bucket=mock_s3_config["bucket_name"],
                    Key="test/file.txt"
                )
                assert response["ContentLength"] == 12

            finally:
                os.unlink(temp_file_path)

    @pytest.mark.asyncio
    async def test_update_media_file_record(self, mock_s3_config):
        """Test updating media file record in database."""
        migrator = FileSystemToS3Migrator(mock_s3_config)

        mock_media_file = Mock()
        mock_media_file.file_uuid = "test-uuid"
        mock_media_file.storage_backend = "filesystem"
        mock_media_file.file_path = "old/path"

        with patch('migrate_filesystem_to_s3.get_db_session') as mock_db_session:
            with patch('migrate_filesystem_to_s3.MediaFile') as mock_media_file_model:
                # Setup mock query
                mock_query = Mock()
                mock_query.filter.return_value.first.return_value = mock_media_file
                mock_db_session.return_value.__enter__.return_value.query.return_value = mock_query

                result = await migrator.update_media_file_record("test-uuid", "new/path")

                assert result is True
                assert mock_media_file.storage_backend == "s3api"
                assert mock_media_file.file_path == "new/path"

    @pytest.mark.asyncio
    async def test_run_migration_dry_run(self, mock_s3_config, temp_content_dir, mock_media_files):
        """Test running migration in dry run mode."""
        migrator = FileSystemToS3Migrator(mock_s3_config)
        migrator.content_dir = Path(temp_content_dir)

        with patch.object(migrator, 'scan_filesystem_files', return_value=[
            {"s3_key": "orgs/test-org-id/courses/test-course-id/activities/video.mp4", "local_path": "test1"}
        ]):
            with patch.object(migrator, 'get_media_files_from_db', return_value=mock_media_files):
                with patch.object(migrator, 'upload_file_to_s3', return_value=True) as mock_upload:
                    with patch.object(migrator, 'update_media_file_record', return_value=True) as mock_update:

                        results = await migrator.run_migration(dry_run=True)

                        assert results["files_to_migrate"] == 1
                        assert results["successful_uploads"] == 1
                        assert results["database_updates"] == 1
                        assert results["failed_uploads"] == 0

                        # Verify no actual uploads or updates were made
                        mock_upload.assert_not_called()
                        mock_update.assert_not_called()

    @pytest.mark.asyncio
    async def test_run_migration_actual(self, mock_s3_config, temp_content_dir, mock_media_files):
        """Test running actual migration."""
        migrator = FileSystemToS3Migrator(mock_s3_config)
        migrator.content_dir = Path(temp_content_dir)

        with patch.object(migrator, 'scan_filesystem_files', return_value=[
            {"s3_key": "orgs/test-org-id/courses/test-course-id/activities/video.mp4", "local_path": "test1"}
        ]):
            with patch.object(migrator, 'get_media_files_from_db', return_value=mock_media_files):
                with patch.object(migrator, 'upload_file_to_s3', return_value=True) as mock_upload:
                    with patch.object(migrator, 'update_media_file_record', return_value=True) as mock_update:

                        results = await migrator.run_migration(dry_run=False)

                        assert results["files_to_migrate"] == 1
                        assert results["successful_uploads"] == 1
                        assert results["database_updates"] == 1
                        assert results["failed_uploads"] == 0

                        # Verify actual uploads and updates were made
                        mock_upload.assert_called_once()
                        mock_update.assert_called_once()