import _ from 'lodash'
import axios from 'axios'
import utils from '@/api/api-utils'
import Vue from 'vue'

export function getMyNoteDrafts() {
  return axios
    .get(`${utils.apiBaseUrl()}/api/note_drafts/my`)
    .then(response => response.data, () => null)
}

export function createNoteDraft(
    attachments: any[],
    body: string,
    sids: any[],
    subject: string,
    title: string,
    topics: string[]
) {
  const data = {body, sids, subject, title, topics}
  _.each(attachments || [], (attachment, index) => data[`attachment[${index}]`] = attachment)
  return utils.postMultipartFormData('/api/note_draft/create', data).then(data => {
    Vue.prototype.$currentUser.myDraftNoteCount++
    return data
  })
}

export function deleteNoteDraft(draftNoteId: number) {
  return axios.delete(`${utils.apiBaseUrl()}/api/note_draft/delete/${draftNoteId}`).then(() => {
    Vue.prototype.$currentUser.myDraftNoteCount--
  })
}

export function renameNoteDraft(draftNoteId: number, title: string) {
  const data = {id: draftNoteId, title: title}
  return axios.post(`${utils.apiBaseUrl()}/api/note_draft/rename`, data).then(response => {
    return response.data
  })
}

export function updateNoteDraft(
    body: string,
    deleteAttachmentIds: number[],
    draftNoteId: number,
    newAttachments: any[],
    subject: string,
    topics: string[]
) {
  const data = {
    body,
    deleteAttachmentIds: deleteAttachmentIds || [],
    id: draftNoteId,
    subject,
    topics,
  }
  _.each(newAttachments || [], (attachment, index) => data[`attachment[${index}]`] = attachment)
  return utils.postMultipartFormData('/api/note_draft/update', data).then(data => {
    return data
  })
}
