from uuid import uuid4
from fastapi import UploadFile
from fastapi import HTTPException

from src.services.media.upload_preparation import prepare_upload


async def upload_org_logo(logo_file, org_uuid):
    contents = logo_file.file.read()
    file_size = len(contents)
    name_in_disk = f"{uuid4()}.{logo_file.filename.split('.')[-1]}"

    upload_response = await prepare_upload(
        file_name=name_in_disk,
        content_type=logo_file.content_type or "image/jpeg",
        file_size=file_size,
        resource_type="org_logo",
        resource_id=org_uuid,
        file_category="image",
    )

    return {
        "name_in_disk": name_in_disk,
        "upload_url": upload_response.upload_url,
        "upload_method": upload_response.method,
        "upload_fields": upload_response.fields,
        "file_url": upload_response.file_url,
    }


async def upload_org_thumbnail(thumbnail_file, org_uuid):
    contents = thumbnail_file.file.read()
    file_size = len(contents)
    name_in_disk = f"{uuid4()}.{thumbnail_file.filename.split('.')[-1]}"

    upload_response = await prepare_upload(
        file_name=name_in_disk,
        content_type=thumbnail_file.content_type or "image/jpeg",
        file_size=file_size,
        resource_type="org_thumbnail",
        resource_id=org_uuid,
        file_category="image",
    )

    return {
        "name_in_disk": name_in_disk,
        "upload_url": upload_response.upload_url,
        "upload_method": upload_response.method,
        "upload_fields": upload_response.fields,
        "file_url": upload_response.file_url,
    }


async def upload_org_preview(file, org_uuid: str):
    contents = file.file.read()
    file_size = len(contents)
    name_in_disk = f"{uuid4()}.{file.filename.split('.')[-1]}"

    upload_response = await prepare_upload(
        file_name=name_in_disk,
        content_type=file.content_type or "image/jpeg",
        file_size=file_size,
        resource_type="org_preview",
        resource_id=org_uuid,
        file_category="image",
    )

    return {
        "name_in_disk": name_in_disk,
        "upload_url": upload_response.upload_url,
        "upload_method": upload_response.method,
        "upload_fields": upload_response.fields,
        "file_url": upload_response.file_url,
    }


async def upload_org_landing_content(file: UploadFile, org_uuid: str):
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided or invalid filename")
        
    contents = file.file.read()
    file_size = len(contents)
    name_in_disk = f"{uuid4()}.{file.filename.split('.')[-1]}"

    # Determine file category based on content type
    content_type = file.content_type or "application/octet-stream"
    if content_type.startswith("image/"):
        file_category = "image"
    elif content_type.startswith("video/"):
        file_category = "video"
    elif content_type == "application/pdf":
        file_category = "pdf"
    else:
        file_category = "document"

    upload_response = await prepare_upload(
        file_name=name_in_disk,
        content_type=content_type,
        file_size=file_size,
        resource_type="org_landing",
        resource_id=org_uuid,
        file_category=file_category,
    )

    return {
        "name_in_disk": name_in_disk,
        "upload_url": upload_response.upload_url,
        "upload_method": upload_response.method,
        "upload_fields": upload_response.fields,
        "file_url": upload_response.file_url,
    }