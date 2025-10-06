from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session
from datetime import datetime

from src.core.events.database import get_db_session
from src.security.auth import get_current_user
from src.services.users.users import PublicUser
from src.services.media.upload_preparation import prepare_upload
from src.db.media.media import MediaFile, MediaFileRead

router = APIRouter()


class UploadPrepareRequest(BaseModel):
    file_name: str
    content_type: str
    file_size: int
    resource_type: str
    resource_id: str
    file_category: Optional[str] = None


class UploadConfirmRequest(BaseModel):
    file_uuid: str
    file_path: str
    file_url: str
    storage_backend: str
    content_type: str
    file_size: int
    resource_type: str
    resource_id: str


@router.post("/prepare")
async def upload_prepare(
    request: UploadPrepareRequest,
    current_user: PublicUser = Depends(get_current_user),
):
    upload_response = await prepare_upload(
        file_name=request.file_name,
        content_type=request.content_type,
        file_size=request.file_size,
        resource_type=request.resource_type,
        resource_id=request.resource_id,
        file_category=request.file_category,
    )
    
    return upload_response



@router.post("/confirm")
async def upload_confirm(
    request: UploadConfirmRequest,
    db_session: Session = Depends(get_db_session),
    current_user: PublicUser = Depends(get_current_user),
) -> MediaFileRead:
    media_file = MediaFile(
        file_uuid=request.file_uuid,
        storage_backend=request.storage_backend,
        file_path=request.file_path,
        file_url=request.file_url,
        content_type=request.content_type,
        file_size=request.file_size,
        resource_type=request.resource_type,
        resource_id=request.resource_id,
        uploaded_at=datetime.utcnow(),
    )
    
    db_session.add(media_file)
    db_session.commit()
    db_session.refresh(media_file)
    
    return MediaFileRead.model_validate(media_file)
