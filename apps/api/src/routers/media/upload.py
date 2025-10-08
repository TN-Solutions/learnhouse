from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session
from datetime import datetime
import logging
from typing import Optional

from src.core.events.database import get_db_session
from src.security.auth import get_current_user
from src.services.users.users import PublicUser
from src.services.media.upload_preparation import prepare_upload
from src.db.media.media import MediaFile, MediaFileRead
from src.services.storage.factory import get_storage_backend

logger = logging.getLogger(__name__)

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
    from src.db.users import User
    from src.db.courses.courses import Course
    from src.db.organizations import Organization
    
    storage_backend = get_storage_backend()
    
    try:
        file_exists = await storage_backend.verify_file_exists(request.file_path)
        
        if not file_exists:
            logger.warning(
                f"File verification failed: file not found in S3",
                extra={
                    "file_uuid": request.file_uuid,
                    "file_path": request.file_path,
                    "resource_type": request.resource_type,
                    "resource_id": request.resource_id,
                }
            )
            raise HTTPException(
                status_code=400,
                detail="File not found in storage. Upload may have failed."
            )
        
        logger.info(
            f"File verification successful",
            extra={
                "file_uuid": request.file_uuid,
                "file_path": request.file_path,
                "resource_type": request.resource_type,
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"File verification error: {str(e)}",
            extra={
                "file_uuid": request.file_uuid,
                "file_path": request.file_path,
                "error": str(e),
            }
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to verify file in storage: {str(e)}"
        )
    
    # Save media file record
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
    
    # Auto-update resource based on resource_type
    try:
        if request.resource_type == "user_avatar":
            user = db_session.query(User).filter(User.user_uuid == request.resource_id).first()
            if user:
                user.avatar_image = request.file_url
                db_session.commit()
                logger.info(f"Updated user avatar: {request.resource_id}")
        
        elif request.resource_type in ["course_thumbnail_image", "course_thumbnail_video"]:
            course = db_session.query(Course).filter(Course.course_uuid == request.resource_id).first()
            if course:
                course.thumbnail_image = request.file_url
                db_session.commit()
                logger.info(f"Updated course thumbnail: {request.resource_id}")
        
        elif request.resource_type == "org_logo":
            org = db_session.query(Organization).filter(Organization.org_uuid == request.resource_id).first()
            if org:
                org.org_image = request.file_url
                db_session.commit()
                logger.info(f"Updated org logo: {request.resource_id}")
        
        elif request.resource_type == "org_thumbnail":
            org = db_session.query(Organization).filter(Organization.org_uuid == request.resource_id).first()
            if org:
                org.org_thumbnail = request.file_url
                db_session.commit()
                logger.info(f"Updated org thumbnail: {request.resource_id}")
        
        elif request.resource_type == "org_preview":
            org = db_session.query(Organization).filter(Organization.org_uuid == request.resource_id).first()
            if org:
                org.org_preview = request.file_url
                db_session.commit()
                logger.info(f"Updated org preview: {request.resource_id}")
    
    except Exception as e:
        logger.error(f"Failed to update resource: {str(e)}")
        # Don't fail the whole request if resource update fails
        pass
    
    return MediaFileRead.model_validate(media_file)
