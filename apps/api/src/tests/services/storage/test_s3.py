import pytest
import os
from unittest.mock import Mock, patch
from moto import mock_aws
import boto3
from botocore.exceptions import ClientError
from src.services.storage.s3 import S3Storage


class TestS3Storage:
    
    @pytest.fixture
    def mock_config(self):
        config = Mock()
        config.hosting_config.content_delivery.s3api.bucket_name = "test-learnhouse-bucket"
        config.hosting_config.content_delivery.s3api.endpoint_url = None
        return config
    
    @pytest.mark.asyncio
    async def test_init_without_bucket_name(self):
        config = Mock()
        config.hosting_config.content_delivery.s3api.bucket_name = None
        config.hosting_config.content_delivery.s3api.endpoint_url = None
        
        with patch('src.services.storage.s3.get_learnhouse_config', return_value=config):
            with pytest.raises(ValueError, match="S3 bucket_name must be configured"):
                S3Storage()
    
    @pytest.mark.asyncio
    async def test_get_upload_url(self, mock_config):
        with mock_aws():
            s3_client = boto3.client("s3", region_name="us-east-1")
            bucket_name = "test-learnhouse-bucket"
            s3_client.create_bucket(Bucket=bucket_name)
            
            with patch('src.services.storage.s3.get_learnhouse_config', return_value=mock_config):
                with patch('src.services.storage.s3.boto3.client', return_value=s3_client):
                    storage = S3Storage()
                    
                    file_path = "test/avatar.png"
                    file_type = "image/png"
                    file_size = 1024
                    
                    result = await storage.get_upload_url(file_path, file_type, file_size)
                    
                    assert result.method == "POST"
                    assert result.upload_url is not None
                    assert "key" in result.fields
                    assert result.fields["key"] == file_path
                    assert bucket_name in result.file_url
                    assert file_path in result.file_url
    
    @pytest.mark.asyncio
    async def test_get_upload_url_default_file_size(self, mock_config):
        with mock_aws():
            s3_client = boto3.client("s3", region_name="us-east-1")
            bucket_name = "test-learnhouse-bucket"
            s3_client.create_bucket(Bucket=bucket_name)
            
            with patch('src.services.storage.s3.get_learnhouse_config', return_value=mock_config):
                with patch('src.services.storage.s3.boto3.client', return_value=s3_client):
                    storage = S3Storage()
                    
                    file_path = "test/document.pdf"
                    file_type = "application/pdf"
                    
                    result = await storage.get_upload_url(file_path, file_type)
                    
                    assert result.method == "POST"
                    assert result.upload_url is not None
                    assert bucket_name in result.file_url
                    assert file_path in result.file_url
    
    @pytest.mark.asyncio
    async def test_get_upload_url_with_custom_endpoint(self):
        config = Mock()
        config.hosting_config.content_delivery.s3api.bucket_name = "test-learnhouse-bucket"
        config.hosting_config.content_delivery.s3api.endpoint_url = "https://s3.example.com"
        
        with mock_aws():
            s3_client = boto3.client("s3", region_name="us-east-1")
            bucket_name = "test-learnhouse-bucket"
            s3_client.create_bucket(Bucket=bucket_name)
            
            with patch('src.services.storage.s3.get_learnhouse_config', return_value=config):
                with patch('src.services.storage.s3.boto3.client', return_value=s3_client):
                    storage = S3Storage()
                    
                    file_path = "test/avatar.png"
                    result = await storage.get_upload_url(file_path, "image/png")
                    
                    assert result.file_url.startswith("https://s3.example.com")
                    assert result.file_url.endswith(f"{bucket_name}/{file_path}")
    
    @pytest.mark.asyncio
    async def test_get_download_url(self, mock_config):
        with mock_aws():
            s3_client = boto3.client("s3", region_name="us-east-1")
            bucket_name = "test-learnhouse-bucket"
            s3_client.create_bucket(Bucket=bucket_name)
            
            file_path = "test/existing_file.png"
            s3_client.put_object(Bucket=bucket_name, Key=file_path, Body=b"test content")
            
            with patch('src.services.storage.s3.get_learnhouse_config', return_value=mock_config):
                with patch('src.services.storage.s3.boto3.client', return_value=s3_client):
                    storage = S3Storage()
                    
                    result = await storage.get_download_url(file_path)
                    
                    assert result is not None
                    assert isinstance(result, str)
                    assert bucket_name in result
                    assert file_path in result
    
    @pytest.mark.asyncio
    async def test_delete_file_success(self, mock_config):
        with mock_aws():
            s3_client = boto3.client("s3", region_name="us-east-1")
            bucket_name = "test-learnhouse-bucket"
            s3_client.create_bucket(Bucket=bucket_name)
            
            file_path = "test/file_to_delete.txt"
            s3_client.put_object(Bucket=bucket_name, Key=file_path, Body=b"test content")
            
            with patch('src.services.storage.s3.get_learnhouse_config', return_value=mock_config):
                with patch('src.services.storage.s3.boto3.client', return_value=s3_client):
                    storage = S3Storage()
                    
                    result = await storage.delete_file(file_path)
                    
                    assert result is True
    
    @pytest.mark.asyncio
    async def test_delete_file_nonexistent(self, mock_config):
        with mock_aws():
            s3_client = boto3.client("s3", region_name="us-east-1")
            bucket_name = "test-learnhouse-bucket"
            s3_client.create_bucket(Bucket=bucket_name)
            
            with patch('src.services.storage.s3.get_learnhouse_config', return_value=mock_config):
                with patch('src.services.storage.s3.boto3.client', return_value=s3_client):
                    storage = S3Storage()
                    
                    file_path = "test/nonexistent.txt"
                    result = await storage.delete_file(file_path)
                    
                    assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_connection_success(self, mock_config):
        with mock_aws():
            s3_client = boto3.client("s3", region_name="us-east-1")
            bucket_name = "test-learnhouse-bucket"
            s3_client.create_bucket(Bucket=bucket_name)
            
            with patch('src.services.storage.s3.get_learnhouse_config', return_value=mock_config):
                with patch('src.services.storage.s3.boto3.client', return_value=s3_client):
                    storage = S3Storage()
                    
                    result = await storage.validate_connection()
                    
                    assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_connection_failure(self, mock_config):
        with patch('src.services.storage.s3.get_learnhouse_config', return_value=mock_config):
            with patch('src.services.storage.s3.boto3.client') as mock_boto_client:
                mock_client = Mock()
                mock_client.head_bucket.side_effect = ClientError(
                    {"Error": {"Code": "404", "Message": "Not Found"}},
                    "HeadBucket"
                )
                mock_boto_client.return_value = mock_client
                
                storage = S3Storage()
                result = await storage.validate_connection()
                
                assert result is False
    
    @pytest.mark.asyncio
    async def test_presigned_url_fields(self, mock_config):
        with mock_aws():
            s3_client = boto3.client("s3", region_name="us-east-1")
            bucket_name = "test-learnhouse-bucket"
            s3_client.create_bucket(Bucket=bucket_name)
            
            with patch('src.services.storage.s3.get_learnhouse_config', return_value=mock_config):
                with patch('src.services.storage.s3.boto3.client', return_value=s3_client):
                    storage = S3Storage()
                    
                    file_path = "test/avatar.png"
                    file_type = "image/png"
                    
                    result = await storage.get_upload_url(file_path, file_type)
                    
                    assert "key" in result.fields
                    assert "Content-Type" in result.fields
                    assert result.fields["Content-Type"] == file_type
