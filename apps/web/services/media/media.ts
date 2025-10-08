import { getBackendUrl } from '@services/config/config'

const LEARNHOUSE_MEDIA_URL = process.env.NEXT_PUBLIC_LEARNHOUSE_MEDIA_URL

function getMediaUrl() {
  if (LEARNHOUSE_MEDIA_URL) {
    return LEARNHOUSE_MEDIA_URL
  } else {
    return getBackendUrl()
  }
}

/**
 * Get media URL from backend response or construct fallback URL
 * This function is storage-agnostic and works with both filesystem and S3
 */
export function getMediaUrlFromFileUrl(fileUrl: string): string {
  // If fileUrl is already a complete URL (S3), return as-is
  if (fileUrl.startsWith('http://') || fileUrl.startsWith('https://')) {
    return fileUrl
  }

  // If fileUrl is a relative path, construct full URL
  if (fileUrl.startsWith('/')) {
    return `${getMediaUrl()}${fileUrl}`
  }

  // If fileUrl is a relative path without leading slash
  return `${getMediaUrl()}/${fileUrl}`
}

// Legacy functions for backward compatibility
// These now use the new getMediaUrlFromFileUrl function

export function getCourseThumbnailMediaDirectory(
  orgUUID: string,
  courseUUID: string,
  fileId: string
) {
  // If fileId is already a full S3 URL, return it directly
  return getMediaUrlFromFileUrl(fileId)
}

export function getOrgLandingMediaDirectory(orgUUID: string, fileId: string) {
  // If fileId is already a full S3 URL, return it directly
  return getMediaUrlFromFileUrl(fileId)
}

export function getUserAvatarMediaDirectory(userUUID: string, fileId: string) {
  // If fileId is already a full S3 URL, return it directly
  return getMediaUrlFromFileUrl(fileId)
}

export function getActivityBlockMediaDirectory(
  orgUUID: string,
  courseId: string,
  activityId: string,
  blockId: any,
  fileId: any,
  type: string
) {
  // If fileId is already a full S3 URL, return it directly
  return getMediaUrlFromFileUrl(fileId)
}

export function getTaskRefFileDir(
  orgUUID: string,
  courseUUID: string,
  activityUUID: string,
  assignmentUUID: string,
  assignmentTaskUUID: string,
  fileID: string
) {
  // If fileID is already a full S3 URL, return it directly
  return getMediaUrlFromFileUrl(fileID)
}

export function getTaskFileSubmissionDir(
  orgUUID: string,
  courseUUID: string,
  activityUUID: string,
  assignmentUUID: string,
  assignmentTaskUUID: string,
  fileSubID: string
) {
  // If fileSubID is already a full S3 URL, return it directly
  return getMediaUrlFromFileUrl(fileSubID)
}

export function getActivityMediaDirectory(
  orgUUID: string,
  courseUUID: string,
  activityUUID: string,
  fileId: string,
  activityType: string
) {
  // If fileId is already a full S3 URL (from activity.content.file_url), return it directly
  // Otherwise construct legacy path for backward compatibility
  return getMediaUrlFromFileUrl(fileId)
}

export function getOrgLogoMediaDirectory(orgUUID: string, fileId: string) {
  // If fileId is already a full S3 URL, return it directly
  return getMediaUrlFromFileUrl(fileId)
}

export function getOrgThumbnailMediaDirectory(orgUUID: string, fileId: string) {
  // If fileId is already a full S3 URL, return it directly
  return getMediaUrlFromFileUrl(fileId)
}

export function getOrgPreviewMediaDirectory(orgUUID: string, fileId: string) {
  // If fileId is already a full S3 URL, return it directly
  return getMediaUrlFromFileUrl(fileId)
}
