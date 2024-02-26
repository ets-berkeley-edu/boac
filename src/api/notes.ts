import _ from 'lodash'
import axios from 'axios'
import ga from '@/lib/ga'
import {useContextStore} from '@/stores/context'
import utils from '@/api/api-utils'

const $_refreshMyDraftNoteCount = () => {
  axios
    .get(`${utils.apiBaseUrl()}/api/notes/my_draft_note_count`)
    .then(
      response => useContextStore().setMyDraftNoteCount(response.data),
      () => null
    )
}
const $_track = action => ga.note(action)

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

export function createDraftNote(sid: string) {
  return axios.post(`${utils.apiBaseUrl()}/api/note/create_draft`, {sid}).then(response => {
    useContextStore().broadcast('note-created',response.data)
    $_refreshMyDraftNoteCount()
    return response.data
  })
}

export function updateNote(
    noteId: number,
    body?: string,
    cohortIds?: number[],
    contactType?: string,
    curatedGroupIds?: number[],
    isDraft?: boolean,
    isPrivate?: boolean,
    setDate?: string,
    sids?: string[],
    subject?: string,
    templateAttachmentIds?: number[],
    topics?: string[]
) {
  const data = {
    id: noteId,
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
  return utils.postMultipartFormData('/api/notes/update', data).then(data => {
    const eventType = _.size(sids) > 1 ? 'notes-batch-published' : 'note-updated'
    useContextStore().broadcast(eventType, data)
    $_track('update')
    $_refreshMyDraftNoteCount()
    return data
  })
}

export function applyNoteTemplate(noteId: number, templateId: number) {
  return axios.post(`${utils.apiBaseUrl()}/api/note/apply_template`, {noteId, templateId}).then(response => {
    const data = response.data
    useContextStore().broadcast('note-updated', data)
    $_track('update')
    $_refreshMyDraftNoteCount()
    return data
  })
}

export function deleteNote(note: any) {
  $_track('delete')
  return axios
    .delete(`${utils.apiBaseUrl()}/api/notes/delete/${note.id}`)
    .then(response => {
      useContextStore().broadcast('note-deleted', note.id)
      $_refreshMyDraftNoteCount()
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
