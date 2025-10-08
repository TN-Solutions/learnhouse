import { getBackendUrl } from '@services/config/config'

export interface UploadPrepareRequest {
  file_name: string
  content_type: string
  file_size: number
  resource_type: string
  resource_id: string
  file_category?: string
}

export interface UploadPrepareResponse {
  file_uuid: string
  file_path: string
  upload_url: string
  method: string
  fields: Record<string, string>
  file_url: string
}

export interface UploadConfirmRequest {
  file_uuid: string
  file_path: string
  file_url: string
  storage_backend: string
  content_type: string
  file_size: number
  resource_type: string
  resource_id: string
}

export async function prepareUpload(
  request: UploadPrepareRequest
): Promise<UploadPrepareResponse> {
  const response = await fetch(`${getBackendUrl()}/api/v1/media/upload/prepare`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to prepare upload')
  }

  return response.json()
}

export async function confirmUpload(
  request: UploadConfirmRequest
): Promise<any> {
  const response = await fetch(`${getBackendUrl()}/api/v1/media/upload/confirm`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to confirm upload')
  }

  return response.json()
}

export async function uploadFileDirect(
  file: File,
  uploadUrl: string,
  method: string,
  fields: Record<string, string>,
  onProgress?: (progress: number) => void
): Promise<void> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()

    // Progress tracking
    if (onProgress) {
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          const progress = (event.loaded / event.total) * 100
          onProgress(progress)
        }
      })
    }

    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve()
      } else {
        reject(new Error(`Upload failed with status ${xhr.status}`))
      }
    })

    xhr.addEventListener('error', () => {
      reject(new Error('Upload failed'))
    })

    xhr.open(method, uploadUrl)

    // For PUT method (R2/S3), send file directly with Content-Type header
    if (method === 'PUT') {
      xhr.setRequestHeader('Content-Type', file.type)
      xhr.send(file)
    } else {
      // For POST method (legacy S3), use FormData with fields
      const formData = new FormData()
      Object.entries(fields).forEach(([key, value]) => {
        formData.append(key, value)
      })
      formData.append('file', file)
      xhr.send(formData)
    }
  })
}


