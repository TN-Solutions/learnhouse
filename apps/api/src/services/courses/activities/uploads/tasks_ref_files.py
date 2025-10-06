from src.services.media.upload_preparation import prepare_upload


async def upload_reference_file(
    file,
    name_in_disk,
    activity_uuid,
    org_uuid,
    course_uuid,
    assignment_uuid,
    assignment_task_uuid,
):
    contents = file.file.read()
    file_size = len(contents)
    
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
        resource_type="assignment_reference",
        resource_id=assignment_task_uuid,
        file_category=file_category,
    )
    
    return {
        "upload_url": upload_response.upload_url,
        "upload_method": upload_response.method,
        "upload_fields": upload_response.fields,
        "file_url": upload_response.file_url,
    }
