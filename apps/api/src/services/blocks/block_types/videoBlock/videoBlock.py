from datetime import datetime
from uuid import uuid4
from src.db.organizations import Organization
from fastapi import HTTPException, status, UploadFile, Request
from sqlmodel import Session, select
from src.db.courses.activities import Activity
from src.db.courses.blocks import Block, BlockRead, BlockTypeEnum
from src.db.courses.courses import Course
from src.services.media.upload_preparation import prepare_upload
from src.services.users.users import PublicUser


async def create_video_block(
    request: Request, video_file: UploadFile, activity_uuid: str, db_session: Session
):
    statement = select(Activity).where(Activity.activity_uuid == activity_uuid)
    activity = db_session.exec(statement).first()

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found"
        )

    block_type = "videoBlock"

    # get org_uuid
    statement = select(Organization).where(Organization.id == activity.org_id)
    org = db_session.exec(statement).first()

    # get course
    statement = select(Course).where(Course.id == activity.course_id)
    course = db_session.exec(statement).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )

    # get block id
    block_uuid = str(f"block_{uuid4()}")

    # Read file content to get actual size
    file_content = await video_file.read()
    file_size = len(file_content)
    
    # Prepare upload using new media service
    upload_response = await prepare_upload(
        file_name=video_file.filename or "video.mp4",
        content_type=video_file.content_type or "video/mp4",
        file_size=file_size,
        resource_type="activity_block",
        resource_id=activity_uuid,
        file_category="video",
    )
    
    # Create block content with file info
    block_content = {
        "file_uuid": upload_response.file_url.split("/")[-1].split(".")[0],  # Extract UUID from URL
        "file_url": upload_response.file_url,
        "file_name": video_file.filename,
        "content_type": video_file.content_type,
        "upload_url": upload_response.upload_url,
        "upload_method": upload_response.method,
        "upload_fields": upload_response.fields,
    }

    # create block
    block = Block(
        activity_id=activity.id,
        block_type=BlockTypeEnum.BLOCK_VIDEO,
        content=block_content,
        org_id=org.id,
        course_id=course.id,
        block_uuid=block_uuid,
        creation_date=str(datetime.now()),
        update_date=str(datetime.now()),
    )

    # insert block
    db_session.add(block)
    db_session.commit()
    db_session.refresh(block)

    block = BlockRead.model_validate(block)

    return block


async def get_video_block(
    request: Request, block_uuid: str, current_user: PublicUser, db_session: Session
):
    statement = select(Block).where(Block.block_uuid == block_uuid)
    block = db_session.exec(statement).first()

    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video file does not exist"
        )

    block = BlockRead.model_validate(block)

    return block
