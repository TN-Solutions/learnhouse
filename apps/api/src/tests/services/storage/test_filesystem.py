import pytest
import os
from unittest.mock import Mock, patch
from src.services.storage.filesystem import FilesystemStorage


class TestFilesystemStorage:
    
    @pytest.fixture
    def mock_config(self):
        config = Mock()
        config.hosting_config.domain = "localhost"
        config.hosting_config.port = 8000
        config.hosting_config.ssl = False
        return config
    
    @pytest.fixture
    def storage(self, mock_config, temp_content_dir):
        with patch('src.services.storage.filesystem.get_learnhouse_config', return_value=mock_config):
            storage_instance = FilesystemStorage()
            return storage_instance
    
    @pytest.mark.asyncio
    async def test_get_upload_url(self, storage, temp_content_dir):
        file_path = "test/avatar.png"
        file_type = "image/png"
        
        result = await storage.get_upload_url(file_path, file_type)
        
        assert result.upload_url == "http://localhost:8000/api/storage/upload"
        assert result.method == "POST"
        assert result.fields["path"] == file_path
        assert result.file_url == f"http://localhost:8000/content/{file_path}"
        
        expected_dir = os.path.join(temp_content_dir, "test")
        assert os.path.exists(expected_dir), "Directory should be created"
    
    @pytest.mark.asyncio
    async def test_get_upload_url_ssl(self, mock_config, temp_content_dir):
        mock_config.hosting_config.ssl = True
        mock_config.hosting_config.port = 443
        
        with patch('src.services.storage.filesystem.get_learnhouse_config', return_value=mock_config):
            storage_instance = FilesystemStorage()
            
            file_path = "test/avatar.png"
            result = await storage_instance.get_upload_url(file_path, "image/png")
            
            assert result.upload_url == "https://localhost/api/storage/upload"
            assert result.file_url == f"https://localhost/content/{file_path}"
    
    @pytest.mark.asyncio
    async def test_get_download_url(self, storage):
        file_path = "test/avatar.png"
        
        result = await storage.get_download_url(file_path)
        
        assert result == f"http://localhost:8000/content/{file_path}"
    
    @pytest.mark.asyncio
    async def test_delete_file_exists(self, storage, temp_content_dir):
        file_path = "test/file_to_delete.txt"
        full_path = os.path.join(temp_content_dir, file_path)
        
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write("test content")
        
        assert os.path.exists(full_path), "File should exist before deletion"
        
        result = await storage.delete_file(file_path)
        
        assert result is True
        assert not os.path.exists(full_path), "File should be deleted"
    
    @pytest.mark.asyncio
    async def test_delete_file_not_exists(self, storage):
        file_path = "test/nonexistent.txt"
        
        result = await storage.delete_file(file_path)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_connection(self, storage, temp_content_dir):
        result = await storage.validate_connection()
        
        assert result is True
        assert os.path.exists(temp_content_dir), "Content directory should exist"
    
    @pytest.mark.asyncio
    async def test_directory_creation(self, storage, temp_content_dir):
        nested_path = "deeply/nested/directory/structure/file.png"
        
        result = await storage.get_upload_url(nested_path, "image/png")
        
        expected_dir = os.path.join(temp_content_dir, "deeply/nested/directory/structure")
        assert os.path.exists(expected_dir), "Nested directories should be created"
        assert result.fields["path"] == nested_path
