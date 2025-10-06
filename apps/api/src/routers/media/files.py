from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from sqlmodel import Session

from src.core.events.database import get_db_session
from src.security.auth import get_current_user
from src.services.users.users import PublicUser
from src.db.media.media import MediaFileRead
from src.services.media.retrieval import (
    get_file_url,
    get_file_metadata,
    get_files_by_resource,
    delete_file,
)

router = APIRouter()


@router.get("/{file_uuid}")
async def get_file_info(
    file_uuid: str,
    generate_presigned: bool = Query(default=True),
    db_session: Session = Depends(get_db_session),
    current_user: PublicUser = Depends(get_current_user),
) -> MediaFileRead:
    file_metadata = await get_file_metadata(file_uuid, db_session)
    
    if generate_presigned and file_metadata.storage_backend == "s3api":
        presigned_url = await get_file_url(file_uuid, db_session, generate_presigned=True)
        file_data = MediaFileRead.model_validate(file_metadata)
        file_data.file_url = presigned_url
        return file_data
    
    return MediaFileRead.model_validate(file_metadata)


@router.get("")
async def list_files(
    resource_type: str = Query(...),
    resource_id: str = Query(...),
    db_session: Session = Depends(get_db_session),
    current_user: PublicUser = Depends(get_current_user),
) -> list[MediaFileRead]:
    files = await get_files_by_resource(resource_type, resource_id, db_session)
    return [MediaFileRead.model_validate(file) for file in files]


@router.delete("/{file_uuid}")
async def delete_file_endpoint(
    file_uuid: str,
    db_session: Session = Depends(get_db_session),
    current_user: PublicUser = Depends(get_current_user),
):
    success = await delete_file(file_uuid, db_session)
    
    if success:
        return {"success": True, "message": "File deleted successfully"}
    
    raise HTTPException(status_code=500, detail="Failed to delete file")
