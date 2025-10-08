import httpx
from src.services.media.upload_preparation import prepare_upload


async def upload_pdf(pdf_file, activity_uuid, org_uuid, course_uuid):
    contents = pdf_file.file.read()
    file_size = len(contents)
    
    try:
        # Step 1: Prepare presigned URL
        upload_response = await prepare_upload(
            file_name=pdf_file.filename or "document.pdf",
            content_type=pdf_file.content_type or "application/pdf",
            file_size=file_size,
            resource_type="activity_pdf",
            resource_id=activity_uuid,
            file_category="pdf",
        )
        
        # Step 2: Upload file to S3 using presigned PUT URL
        async with httpx.AsyncClient() as client:
            response = await client.put(
                upload_response["upload_url"],
                content=contents,
                headers={"Content-Type": pdf_file.content_type or "application/pdf"},
                timeout=300.0  # 5 minutes timeout for large files
            )
            
            if response.status_code not in [200, 204]:
                raise Exception(f"S3 upload failed with status {response.status_code}: {response.text}")
        
        return {
            "upload_url": upload_response["upload_url"],
            "upload_method": upload_response["method"],
            "upload_fields": upload_response.get("fields", {}),
            "file_url": upload_response["file_url"],
        }

    except Exception as e:
        return {"message": f"There was an error uploading the file: {str(e)}"}
