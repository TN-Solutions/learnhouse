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
  const legacyPath = `content/orgs/${orgUUID}/courses/${courseUUID}/thumbnails/${fileId}`
  return getMediaUrlFromFileUrl(legacyPath)
}

export function getOrgLandingMediaDirectory(orgUUID: string, fileId: string) {
  const legacyPath = `content/orgs/${orgUUID}/landing/${fileId}`
  return getMediaUrlFromFileUrl(legacyPath)
}

export function getUserAvatarMediaDirectory(userUUID: string, fileId: string) {
  const legacyPath = `content/users/${userUUID}/avatars/${fileId}`
  return getMediaUrlFromFileUrl(legacyPath)
}

export function getActivityBlockMediaDirectory(
  orgUUID: string,
  courseId: string,
  activityId: string,
  blockId: any,
  fileId: any,
  type: string
) {
  let legacyPath = ''
  if (type == 'pdfBlock') {
    legacyPath = `content/orgs/${orgUUID}/courses/${courseId}/activities/${activityId}/dynamic/blocks/pdfBlock/${blockId}/${fileId}`
  } else if (type == 'videoBlock') {
    legacyPath = `content/orgs/${orgUUID}/courses/${courseId}/activities/${activityId}/dynamic/blocks/videoBlock/${blockId}/${fileId}`
  } else if (type == 'imageBlock') {
    legacyPath = `content/orgs/${orgUUID}/courses/${courseId}/activities/${activityId}/dynamic/blocks/imageBlock/${blockId}/${fileId}`
  }

  return getMediaUrlFromFileUrl(legacyPath)
}

export function getTaskRefFileDir(
  orgUUID: string,
  courseUUID: string,
  activityUUID: string,
  assignmentUUID: string,
  assignmentTaskUUID: string,
  fileID: string
) {
  const legacyPath = `content/orgs/${orgUUID}/courses/${courseUUID}/activities/${activityUUID}/assignments/${assignmentUUID}/tasks/${assignmentTaskUUID}/${fileID}`
  return getMediaUrlFromFileUrl(legacyPath)
}

export function getTaskFileSubmissionDir(
  orgUUID: string,
  courseUUID: string,
  activityUUID: string,
  assignmentUUID: string,
  assignmentTaskUUID: string,
  fileSubID: string
) {
  const legacyPath = `content/orgs/${orgUUID}/courses/${courseUUID}/activities/${activityUUID}/assignments/${assignmentUUID}/tasks/${assignmentTaskUUID}/subs/${fileSubID}`
  return getMediaUrlFromFileUrl(legacyPath)
}

export function getActivityMediaDirectory(
  orgUUID: string,
  courseUUID: string,
  activityUUID: string,
  fileId: string,
  activityType: string
) {
  let legacyPath = ''
  if (activityType == 'video') {
    legacyPath = `content/orgs/${orgUUID}/courses/${courseUUID}/activities/${activityUUID}/video/${fileId}`
  } else if (activityType == 'documentpdf') {
    legacyPath = `content/orgs/${orgUUID}/courses/${courseUUID}/activities/${activityUUID}/documentpdf/${fileId}`
  }

  return getMediaUrlFromFileUrl(legacyPath)
}

export function getOrgLogoMediaDirectory(orgUUID: string, fileId: string) {
  const legacyPath = `content/orgs/${orgUUID}/logos/${fileId}`
  return getMediaUrlFromFileUrl(legacyPath)
}

export function getOrgThumbnailMediaDirectory(orgUUID: string, fileId: string) {
  const legacyPath = `content/orgs/${orgUUID}/thumbnails/${fileId}`
  return getMediaUrlFromFileUrl(legacyPath)
}

export function getOrgPreviewMediaDirectory(orgUUID: string, fileId: string) {
  const legacyPath = `content/orgs/${orgUUID}/previews/${fileId}`
  return getMediaUrlFromFileUrl(legacyPath)
}
