import sys
import os
import pytest
import tempfile
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

os.environ["TESTING"] = "true"

os.environ["LOGFIRE_IGNORE_NO_CONFIG"] = "1" 


@pytest.fixture
def temp_content_dir():
    temp_dir = tempfile.mkdtemp(prefix="learnhouse_test_")
    original_cwd = os.getcwd()
    content_dir = os.path.join(temp_dir, "content")
    os.makedirs(content_dir, exist_ok=True)
    
    os.chdir(temp_dir)
    
    yield content_dir
    
    os.chdir(original_cwd)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_s3_environment():
    try:
        from moto import mock_aws
    except ImportError:
        pytest.skip("moto not installed")
    
    with mock_aws():
        import boto3
        s3_client = boto3.client("s3", region_name="us-east-1")
        bucket_name = "test-learnhouse-bucket"
        s3_client.create_bucket(Bucket=bucket_name)
        yield s3_client, bucket_name
