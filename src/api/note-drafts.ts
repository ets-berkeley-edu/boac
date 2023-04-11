import _ from 'lodash'
import axios from 'axios'
import utils from '@/api/api-utils'
import Vue from 'vue'

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

export function getMyNoteDrafts() {
  return axios
    .get(`${utils.apiBaseUrl()}/api/note_drafts/my`)
    .then(response => response.data, () => null)
}

export function getNoteDraft(noteId) {
  return axios.get(`${utils.apiBaseUrl()}/api/note_draft/${noteId}`).then(response => response.data, () => null)
}

export function updateNoteDraft(
    body: string,
    contactType: string,
    deleteAttachmentIds: number[],
    draftNoteId: number,
    isPrivate: boolean,
    newAttachments: any[],
    setDate: string,
    subject: string,
    topics: string[]
) {
  const data = {
    body,
    contactType,
    deleteAttachmentIds: deleteAttachmentIds || [],
    id: draftNoteId,
    isPrivate,
    setDate,
    subject,
    topics,
  }
  _.each(newAttachments || [], (attachment, index) => data[`attachment[${index}]`] = attachment)
  return utils.postMultipartFormData('/api/note_draft/update', data).then(data => {
    return data
  })
}
