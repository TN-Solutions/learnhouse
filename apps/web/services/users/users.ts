import { getAPIUrl } from '@services/config/config'
import {
  RequestBody,
  RequestBodyWithAuthHeader,
  errorHandling,
  getResponseMetadata,
} from '@services/utils/ts/requests'

export async function getUser(user_id: string, access_token?: string) {
  const result = await fetch(
    `${getAPIUrl()}users/id/${user_id}`,
    access_token ? RequestBodyWithAuthHeader('GET', null, null, access_token) : RequestBody('GET', null, null)
  )
  const res = await errorHandling(result)
  return res
}

export async function getUserByUsername(username: string, access_token?: string) {
  const result = await fetch(
    `${getAPIUrl()}users/username/${username}`,
    access_token ? RequestBodyWithAuthHeader('GET', null, null, access_token) : RequestBody('GET', null, null)
  )
  const res = await errorHandling(result)
  return res
}

export async function getCoursesByUser(user_id: string, access_token?: string) {
  const result = await fetch(
    `${getAPIUrl()}users/${user_id}/courses`,
    access_token ? RequestBodyWithAuthHeader('GET', null, null, access_token) : RequestBody('GET', null, null)
  )
  const res = await getResponseMetadata(result)
  return res
}
