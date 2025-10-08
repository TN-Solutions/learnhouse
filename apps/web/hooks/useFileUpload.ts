import { useState, useCallback } from 'react'
import {
  prepareUpload,
  confirmUpload,
  uploadFileDirect,
  UploadPrepareRequest,
  UploadPrepareResponse,
} from '@services/media/upload'

export interface UploadOptions {
  file: File
  resourceType: string
  resourceId: string
  fileCategory?: string
  onProgress?: (progress: number) => void
}

export interface UploadResult {
  fileUrl: string
  success: boolean
  error?: string
}

export interface UseFileUploadReturn {
  upload: (options: UploadOptions) => Promise<UploadResult>
  isLoading: boolean
  progress: number
  error: string | null
}

export function useFileUpload(): UseFileUploadReturn {
  const [isLoading, setIsLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)

  const upload = useCallback(
    async (options: UploadOptions): Promise<UploadResult> => {
      const { file, resourceType, resourceId, fileCategory, onProgress } =
        options

      setIsLoading(true)
      setProgress(0)
      setError(null)

      try {
        // Step 1: Prepare upload
        const prepareRequest: UploadPrepareRequest = {
          file_name: file.name,
          content_type: file.type,
          file_size: file.size,
          resource_type: resourceType,
          resource_id: resourceId,
          file_category: fileCategory,
        }

        const uploadResponse: UploadPrepareResponse =
          await prepareUpload(prepareRequest)

        // Step 2: Upload file to S3
        await uploadFileDirect(
          file,
          uploadResponse.upload_url,
          uploadResponse.method,
          uploadResponse.fields,
          (progressValue) => {
            setProgress(progressValue)
            onProgress?.(progressValue)
          }
        )

        // Step 3: Confirm upload
        await confirmUpload({
          file_uuid: uploadResponse.file_uuid,
          file_path: uploadResponse.file_path,
          file_url: uploadResponse.file_url,
          storage_backend: 's3api',
          content_type: file.type,
          file_size: file.size,
          resource_type: resourceType,
          resource_id: resourceId,
        })

        setProgress(100)
        return {
          fileUrl: uploadResponse.file_url,
          success: true,
        }
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : 'Upload failed'
        setError(errorMessage)
        return {
          fileUrl: '',
          success: false,
          error: errorMessage,
        }
      } finally {
        setIsLoading(false)
      }
    },
    []
  )

  return {
    upload,
    isLoading,
    progress,
    error,
  }
}

export function useFileUploadMultiple() {
  const [isLoading, setIsLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)

  const uploadMultiple = useCallback(
    async (
      optionsList: UploadOptions[],
      onProgress?: (fileProgress: number, totalProgress: number) => void
    ): Promise<UploadResult[]> => {
      setIsLoading(true)
      setProgress(0)
      setError(null)

      const results: UploadResult[] = []

      try {
        for (let i = 0; i < optionsList.length; i++) {
          const options = optionsList[i]
          const fileProgress = (i / optionsList.length) * 100
          const totalProgress = ((i + 1) / optionsList.length) * 100

          onProgress?.(fileProgress, totalProgress)
          setProgress(totalProgress)

          // Use the single upload hook logic
          const { file, resourceType, resourceId, fileCategory } = options

          const prepareRequest: UploadPrepareRequest = {
            file_name: file.name,
            content_type: file.type,
            file_size: file.size,
            resource_type: resourceType,
            resource_id: resourceId,
            file_category: fileCategory,
          }

          const uploadResponse: UploadPrepareResponse =
            await prepareUpload(prepareRequest)

          // S3 upload
          await uploadFileDirect(
            file,
            uploadResponse.upload_url,
            uploadResponse.method,
            uploadResponse.fields
          )

          await confirmUpload({
            file_uuid: uploadResponse.file_uuid,
            file_path: uploadResponse.file_path,
            file_url: uploadResponse.file_url,
            storage_backend: 's3api',
            content_type: file.type,
            file_size: file.size,
            resource_type: resourceType,
            resource_id: resourceId,
          })

          results.push({
            fileUrl: uploadResponse.file_url,
            success: true,
          })
        }

        setProgress(100)
        return results
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : 'Upload failed'
        setError(errorMessage)

        // Return results with error for failed uploads
        return results.map((result) =>
          result.success
            ? result
            : {
                fileUrl: '',
                success: false,
                error: errorMessage,
              }
        )
      } finally {
        setIsLoading(false)
      }
    },
    []
  )

  return {
    uploadMultiple,
    isLoading,
    progress,
    error,
  }
}
