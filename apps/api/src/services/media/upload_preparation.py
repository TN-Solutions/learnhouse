import os
import re
from uuid import uuid4
from typing import Optional
from fastapi import HTTPException

from src.services.storage.factory import get_storage_backend
from src.services.storage.base import UploadUrlResponse


ALLOWED_MIME_TYPES = {
    "image": ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"],
    "video": ["video/mp4", "video/webm", "video/ogg"],
    "pdf": ["application/pdf"],
    "document": ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
}

ALLOWED_EXTENSIONS = {
    "image": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
    "video": [".mp4", ".webm", ".ogg"],
    "pdf": [".pdf"],
    "document": [".pdf", ".doc", ".docx"],
}

MAX_FILE_SIZE = 104857600


def sanitize_filename(filename: str) -> str:
    filename = os.path.basename(filename)
    filename = re.sub(r'[^\w\s\-\.]', '_', filename)
    filename = re.sub(r'\.\.+', '.', filename)
    
    if not filename or filename.startswith('.'):
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    return filename


def validate_file_type(content_type: str, filename: str, file_category: Optional[str] = None) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    
    if file_category:
        allowed_types = ALLOWED_MIME_TYPES.get(file_category, [])
        allowed_exts = ALLOWED_EXTENSIONS.get(file_category, [])
        
        if content_type not in allowed_types or ext not in allowed_exts:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed for {file_category}. Allowed types: {', '.join(allowed_exts)}"
            )
    
    return True


def validate_file_size(file_size: int, max_size: int = MAX_FILE_SIZE) -> bool:
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {max_size / 1024 / 1024}MB"
        )
    return True


async def prepare_upload(
    file_name: str,
    content_type: str,
    file_size: int,
    resource_type: str,
    resource_id: str,
    file_category: Optional[str] = None,
) -> dict:
    sanitized_filename = sanitize_filename(file_name)
    
    validate_file_type(content_type, sanitized_filename, file_category)
    validate_file_size(file_size)
    
    file_uuid = str(uuid4())
    file_extension = os.path.splitext(sanitized_filename)[1]
    stored_filename = f"{file_uuid}{file_extension}"
    
    file_path = f"{resource_type}/{resource_id}/{stored_filename}"
    
    storage_backend = get_storage_backend()
    
    upload_response = await storage_backend.get_upload_url(
        file_path=file_path,
        file_type=content_type,
        file_size=file_size,
    )
    
    return {
        "file_uuid": file_uuid,
        "upload_url": upload_response.upload_url,
        "method": upload_response.method,
        "fields": upload_response.fields,
        "file_url": upload_response.file_url,
        "file_path": file_path,
    }
