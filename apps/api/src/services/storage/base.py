from abc import ABC, abstractmethod
from typing import Dict, Optional
from pydantic import BaseModel


class UploadUrlResponse(BaseModel):
    upload_url: str
    method: str
    fields: Dict[str, str]
    file_url: str


class StorageBackend(ABC):
    @abstractmethod
    async def get_upload_url(
        self,
        file_path: str,
        file_type: str,
        file_size: Optional[int] = None,
    ) -> UploadUrlResponse:
        pass

    @abstractmethod
    async def get_download_url(self, file_path: str) -> str:
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        pass
