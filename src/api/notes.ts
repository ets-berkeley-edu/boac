import _ from 'lodash'
import axios from 'axios'
import utils from '@/api/api-utils'
import Vue from 'vue'

const $_track = action => Vue.prototype.$ga.note(action)

export function getNote(noteId) {
  $_track('view')
  return axios
    .get(`${utils.apiBaseUrl()}/api/note/${noteId}`)
    .then(response => response.data, () => null)
}

export function getMyDraftNotes() {
  return axios
    .get(`${utils.apiBaseUrl()}/api/notes/my_drafts`)
    .then(response => response.data, () => null)
}

export function markNoteRead(noteId) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/notes/${noteId}/mark_read`)
    .then(response => {
      $_track('read')
      return response.data
    }, () => null)
}

export function createNotes(
    attachments: any[],
    body: string,
    cohortIds: number[],
    contactType: string,
    curatedGroupIds: number[],
    isDraft: boolean,
    isPrivate: boolean,
    setDate: string,
    sids: any,
    subject: string,
    templateAttachmentIds: [],
    topics: string[]
) {
  const data = {
    body,
    cohortIds,
    contactType,
    curatedGroupIds,
    isDraft,
    isPrivate,
    setDate,
    sids,
    subject,
    templateAttachmentIds,
    topics
  }
  _.each(attachments || [], (attachment, index) => data[`attachment[${index}]`] = attachment)
  const action = sids.length > 1 ? 'batch' : 'create'
  $_track(isPrivate ? `${action} private` : action)
  return utils.postMultipartFormData('/api/notes/create', data).then(() => {
    if (isDraft) {
      Vue.prototype.$eventHub.emit('draft-note-created')
      Vue.prototype.$currentUser.myDraftNoteCount++
    }
  })
}

export function updateNote(
    body: string,
    contactType: string,
    isDraft: boolean,
    isPrivate: boolean,
    noteId: number,
    setDate: string,
    subject: string,
    topics: string[]
) {
  const data = {
    body,
    contactType,
    id: noteId,
    isDraft,
    isPrivate,
    setDate,
    subject,
    topics
  }
  const api_json = utils.postMultipartFormData('/api/notes/update', data)
  $_track('update')
  return api_json
}

export function deleteNote(note: any) {
  $_track('delete')
  return axios
    .delete(`${utils.apiBaseUrl()}/api/notes/delete/${note.id}`)
    .then(response => {
      Vue.prototype.$eventHub.emit('advising-note-deleted', note.id)
      if (note.isDraft) {
        Vue.prototype.$currentUser.myDraftNoteCount = Vue.prototype.$currentUser.myDraftNoteCount - 1
      }
      return response.data
    })
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
