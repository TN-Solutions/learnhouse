import pytest
from unittest.mock import Mock, patch
from src.services.storage.factory import get_storage_backend, reset_storage_backend
from src.services.storage.s3 import S3Storage


class TestStorageFactory:

    def test_get_storage_backend_returns_s3_storage(self):
        """Test that factory always returns S3Storage instance."""
        # Reset cache
        reset_storage_backend()

        with patch('src.services.storage.s3.get_learnhouse_config'):
            storage = get_storage_backend()

        assert isinstance(storage, S3Storage)

    def test_get_storage_backend_caches_instance(self):
        """Test that factory caches the storage backend instance."""
        # Reset cache
        reset_storage_backend()

        with patch('src.services.storage.s3.get_learnhouse_config'):
            storage1 = get_storage_backend()
            storage2 = get_storage_backend()

        assert storage1 is storage2
        assert isinstance(storage1, S3Storage)

    def test_reset_storage_backend_clears_cache(self):
        """Test that reset_storage_backend clears the cache."""
        # Get first instance
        with patch('src.services.storage.s3.get_learnhouse_config'):
            storage1 = get_storage_backend()

        # Reset cache
        reset_storage_backend()

        # Get new instance
        with patch('src.services.storage.s3.get_learnhouse_config'):
            storage2 = get_storage_backend()

        assert storage1 is not storage2
        assert isinstance(storage2, S3Storage)