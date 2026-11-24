import axios from 'axios'
import type {InvalidUserTag, TagContext, TaggableUser} from '@/lib/types'
import utils from '@/api/api-utils'

// Looks up users the author may tag at the current cursor. The request is never cancelled, so a slow answer still finishes
// and the caller can cache it.
export function findTaggableUsers(snippet: string, context: TagContext): Promise<TaggableUser[]> {
  const url: string = `${utils.apiBaseUrl()}/api/users/taggable`
  return axios.post(url, {snippet, ...context}).then(response => response.data)
}

export function listUserTags() {
  const url: string = `${utils.apiBaseUrl()}/api/user_tag/list`
  return axios.get(url).then(response => response.data)
}

export function markUserTagRead(userTagId: number) {
  return updateUserTag(userTagId, {readByUser: true})
}

export function markUserTagUnread(userTagId: number) {
  return updateUserTag(userTagId, {readByUser: false})
}

function updateUserTag(userTagId: number, changes: {readByUser: boolean}) {
  const url: string = `${utils.apiBaseUrl()}/api/user_tag/${userTagId}`
  return axios.patch(url, changes).then(response => response.data)
}

// Checks the UIDs tagged in a note or comment before it is saved and returns the ones the backend would reject.
export function validateUserTags(uids: string[], context: TagContext): Promise<InvalidUserTag[]> {
  const url: string = `${utils.apiBaseUrl()}/api/users/tags/validate`
  return axios.post(url, {uids, ...context}).then(response => response.data)
}
