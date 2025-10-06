from src.services.media.upload_preparation import prepare_upload


async def upload_pdf(pdf_file, activity_uuid, org_uuid, course_uuid):
    contents = pdf_file.file.read()
    file_size = len(contents)
    
    try:
        upload_response = await prepare_upload(
            file_name=pdf_file.filename or "document.pdf",
            content_type=pdf_file.content_type or "application/pdf",
            file_size=file_size,
            resource_type="activity_pdf",
            resource_id=activity_uuid,
            file_category="pdf",
        )
        
        return {
            "upload_url": upload_response.upload_url,
            "upload_method": upload_response.method,
            "upload_fields": upload_response.fields,
            "file_url": upload_response.file_url,
        }

    except Exception as e:
        return {"message": f"There was an error uploading the file: {str(e)}"}
