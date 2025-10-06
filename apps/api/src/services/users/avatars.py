from src.services.media.upload_preparation import prepare_upload


async def upload_avatar(avatar_file, name_in_disk, user_uuid):
    contents = avatar_file.file.read()
    file_size = len(contents)
    
    try:
        upload_response = await prepare_upload(
            file_name=name_in_disk,
            content_type=avatar_file.content_type or "image/jpeg",
            file_size=file_size,
            resource_type="user_avatar",
            resource_id=user_uuid,
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
