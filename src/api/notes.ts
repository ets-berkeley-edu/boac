import _ from 'lodash'
import axios from 'axios'
import utils from '@/api/api-utils'
import Vue from 'vue'

export function getNote(noteId) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/note/${noteId}`)
    .then(response => response.data, () => null)
}

export function markNoteRead(noteId) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/notes/${noteId}/mark_read`)
    .then(response => {
      const uid = Vue.prototype.$currentUser.uid
      Vue.prototype.$ga.noteEvent(noteId, `Advisor ${uid} read a note`, 'read')
      return response.data
    }, () => null)
}

export function createNotes(
    attachments: any[],
    body: string,
    cohortIds: number[],
    curatedGroupIds: number[],
    isPrivate: boolean,
    sids: any,
    subject: string,
    templateAttachmentIds: [],
    topics: string[]
) {
  const data = {
    body,
    cohortIds,
    curatedGroupIds,
    isPrivate,
    sids,
    subject,
    templateAttachmentIds,
    topics
  }
  _.each(attachments || [], (attachment, index) => data[`attachment[${index}]`] = attachment)
  return utils.postMultipartFormData('/api/notes/create', data)
}

export function updateNote(
    body: string,
    isPrivate: boolean,
    noteId: number,
    subject: string,
    topics: string[]
) {
  const data = {
    body: body,
    id: noteId,
    isPrivate: isPrivate,
    subject: subject,
    topics: topics
  }
  const api_json = utils.postMultipartFormData('/api/notes/update', data)
  const uid = Vue.prototype.$currentUser.uid
  Vue.prototype.$ga.noteEvent(noteId, `Advisor ${uid} updated a note`, 'update')
  return api_json
}

export function deleteNote(noteId: number) {
  return axios
    .delete(`${utils.apiBaseUrl()}/api/notes/delete/${noteId}`)
    .then(response => response.data)
}

export function addAttachments(noteId: number, attachments: any[]) {
  const data = {}
  _.each(attachments, (attachment, index) => data[`attachment[${index}]`] = attachment)
  return utils.postMultipartFormData(`/api/notes/${noteId}/attachments`, data)
}

export function removeAttachment(noteId: number, attachmentId: number) {
  return axios
    .delete(`${utils.apiBaseUrl()}/api/notes/${noteId}/attachment/${attachmentId}`)
    .then(response => response.data)
}
