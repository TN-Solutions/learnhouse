import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from typing import Optional

from src.services.storage.base import StorageBackend, UploadUrlResponse
from config.config import get_learnhouse_config


class S3Storage(StorageBackend):
    def __init__(self):
        self.config = get_learnhouse_config()
        s3_config = self.config.hosting_config.content_delivery.s3api
        
        if not s3_config.bucket_name:
            raise ValueError("S3 bucket_name must be configured")
        
        self.bucket_name = s3_config.bucket_name
        self.endpoint_url = s3_config.endpoint_url
        
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            config=Config(signature_version="s3v4"),
        )

    async def get_upload_url(
        self,
        file_path: str,
        file_type: str,
        file_size: Optional[int] = None,
    ) -> UploadUrlResponse:
        try:
            max_file_size = file_size if file_size else 104857600
            
            presigned_post = self.s3_client.generate_presigned_post(
                Bucket=self.bucket_name,
                Key=file_path,
                Fields={"Content-Type": file_type},
                Conditions=[
                    {"Content-Type": file_type},
                    ["content-length-range", 0, max_file_size],
                ],
                ExpiresIn=3600,
            )

            file_url = f"{self.endpoint_url}/{self.bucket_name}/{file_path}" if self.endpoint_url else f"https://{self.bucket_name}.s3.amazonaws.com/{file_path}"

            return UploadUrlResponse(
                upload_url=presigned_post["url"],
                method="POST",
                fields=presigned_post["fields"],
                file_url=file_url,
            )
        except ClientError as e:
            raise Exception(f"Failed to generate presigned POST URL: {str(e)}")

    async def get_download_url(self, file_path: str) -> str:
        try:
            presigned_url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": file_path},
                ExpiresIn=3600,
            )
            return presigned_url
        except ClientError as e:
            raise Exception(f"Failed to generate presigned GET URL: {str(e)}")

    async def delete_file(self, file_path: str) -> bool:
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except ClientError as e:
            print(f"Error deleting S3 file: {e}")
            return False

    async def validate_connection(self) -> bool:
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError as e:
            print(f"S3 storage validation failed: {e}")
            return False
