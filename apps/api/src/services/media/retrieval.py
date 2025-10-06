from typing import Optional
from sqlmodel import Session, select
from fastapi import HTTPException

from src.db.media.media import MediaFile
from src.services.storage.factory import get_storage_backend


async def get_file_url(
    file_uuid: str,
    db: Session,
    generate_presigned: bool = True,
) -> str:
    statement = select(MediaFile).where(MediaFile.file_uuid == file_uuid)
    result = db.exec(statement).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="File not found")
    
    # S3-only storage implementation
    if result.storage_backend == "s3api" and generate_presigned:
        storage_backend = get_storage_backend()
        presigned_url = await storage_backend.get_download_url(result.file_path)
        return presigned_url
    
    return result.file_url


async def get_file_metadata(
    file_uuid: str,
    db: Session,
) -> Optional[MediaFile]:
    statement = select(MediaFile).where(MediaFile.file_uuid == file_uuid)
    result = db.exec(statement).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="File not found")
    
    return result


async def get_files_by_resource(
    resource_type: str,
    resource_id: str,
    db: Session,
) -> list[MediaFile]:
    statement = select(MediaFile).where(
        MediaFile.resource_type == resource_type,
        MediaFile.resource_id == resource_id,
    )
    results = db.exec(statement).all()
    return list(results)


async def delete_file(
    file_uuid: str,
    db: Session,
) -> bool:
    statement = select(MediaFile).where(MediaFile.file_uuid == file_uuid)
    result = db.exec(statement).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="File not found")
    
    storage_backend = get_storage_backend()
    deleted = await storage_backend.delete_file(result.file_path)
    
    if deleted:
        db.delete(result)
        db.commit()
        return True
    
    raise HTTPException(status_code=500, detail="Failed to delete file from storage")
