import axios from 'axios'
import ga from '@/lib/ga'
import utils from '@/api/api-utils'
import {each, size, toNumber} from 'lodash'
import {useContextStore} from '@/stores/context'

const $_refreshMyDraftNoteCount = () => {
  axios.get(`${utils.apiBaseUrl()}/api/notes/my_draft_note_count`).then(response => {
    useContextStore().setMyDraftNoteCount(toNumber(response.data))
  })
}
const $_track = action => ga.note(action)

export function getNote(noteId: number) {
  $_track('view')
  const url: string = `${utils.apiBaseUrl()}/api/note/${noteId}`
  return axios.get(url).then(response => response.data)
}

export function getMyDraftNotes() {
  const url: string = `${utils.apiBaseUrl()}/api/notes/my_drafts`
  return axios.get(url).then(response => response.data)
}

export function markNoteRead(noteId: number) {
  return axios.post(`${utils.apiBaseUrl()}/api/notes/${noteId}/mark_read`).then(response => {
    $_track('read')
    return response.data
  })
}

export function createDraftNote(sid: string) {
  return axios.post(`${utils.apiBaseUrl()}/api/note/create_draft`, {sid}).then(response => {
    const data = response.data
    useContextStore().broadcast('note-created', data)
    $_refreshMyDraftNoteCount()
    return data
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
  const args = {
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
  return utils.postMultipartFormData('/api/notes/update', args).then(data => {
    const eventType = size(sids) > 1 ? 'notes-batch-published' : 'note-updated'
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
  return axios.delete(`${utils.apiBaseUrl()}/api/notes/delete/${note.id}`).then(response => {
    useContextStore().broadcast('note-deleted', note.id)
    $_refreshMyDraftNoteCount()
    return response.data
  })
}

export function addAttachments(noteId: number, attachments: any[]) {
  const data = {}
  each(attachments, (attachment, index) => data[`attachment[${index}]`] = attachment)
  return new Promise(resolve => {
    utils.postMultipartFormData(`/api/notes/${noteId}/attachments`, data).then(note => {
      useContextStore().broadcast('note-updated', note)
      resolve(note)
    })
  })
}

export function removeAttachment(noteId: number, attachmentId: number) {
  return axios.delete(`${utils.apiBaseUrl()}/api/notes/${noteId}/attachment/${attachmentId}`).then(response => {
    const note = response.data
    useContextStore().broadcast('note-updated', note)
    return note
  })
}
