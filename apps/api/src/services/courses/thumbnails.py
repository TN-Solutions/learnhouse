from src.services.media.upload_preparation import prepare_upload


async def upload_thumbnail(thumbnail_file, name_in_disk, org_uuid, course_id):
    contents = thumbnail_file.file.read()
    file_size = len(contents)
    
    try:
        upload_response = await prepare_upload(
            file_name=name_in_disk,
            content_type=thumbnail_file.content_type or "image/jpeg",
            file_size=file_size,
            resource_type="course_thumbnail",
            resource_id=course_id,
            file_category="image",
        )
        
        return {
            "upload_url": upload_response.upload_url,
            "upload_method": upload_response.method,
            "upload_fields": upload_response.fields,
            "file_url": upload_response.file_url,
        }

    except Exception as e:
        return {"message": f"There was an error uploading the file: {str(e)}"}
