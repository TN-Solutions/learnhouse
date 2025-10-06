from typing import Optional

from config.config import get_learnhouse_config
from src.services.storage.base import StorageBackend
from src.services.storage.s3 import S3Storage

_storage_backend_cache: Optional[StorageBackend] = None


def get_storage_backend() -> StorageBackend:
    """
    Get the storage backend instance.
    Always returns S3Storage since filesystem storage has been removed.
    """
    global _storage_backend_cache

    if _storage_backend_cache is not None:
        return _storage_backend_cache

    _storage_backend_cache = S3Storage()
    return _storage_backend_cache


def reset_storage_backend():
    global _storage_backend_cache
    _storage_backend_cache = None
