import axios from 'axios'
import {each, size, toNumber} from 'lodash'
import ga from '@/lib/ga'
import utils from '@/api/api-utils'
import type {Note, NoteAttachment, NoteEditSessionModel} from '@/lib/types'
import {isPeerAdvisor} from '@/lib/boa-user'
import {useContextStore} from '@/stores/context'

const $_refreshMyDraftNoteCount = () => {
  const contextStore = useContextStore()
  if (!isPeerAdvisor(contextStore.currentUser)) {
    axios.get(`${utils.apiBaseUrl()}/api/notes/my_draft_note_count`).then(response => {
      contextStore.setMyDraftNoteCount(toNumber(response.data))
    })
  }
}
const $_track = action => ga.note(action)

export function addNoteComment(parentNoteId: number, text: string, attachments: NoteAttachment[]) {
  const args = {
    body: text,
    parentNoteId: parentNoteId
  }
  const contextStore = useContextStore()
  each(attachments, (attachment, index) => args[`attachment[${index}]`] = attachment)
  return utils.postMultipartFormData('/api/notes/add_comment', args).then(data => {
    contextStore.broadcast('note-updated', data)
    $_track('update')
    return data
  })
}

export function getNote(noteId: number) {
  $_track('view')
  const currentUser = useContextStore().currentUser
  const apiPath: string = isPeerAdvisor(currentUser) ? '/api/peer_advising/note/' : '/api/note/'
  const url: string = `${utils.apiBaseUrl()}${apiPath}${noteId}`
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
    contactType?: string | null,
    curatedGroupIds?: number[],
    isDraft?: boolean,
    isPrivate?: boolean,
    setDate?: string,
    sids?: string[],
    subject?: string,
    templateAttachmentIds?: number[],
    topics?: string[],
    noteTemplateId?: number,
    attachments?: NoteAttachment[],
    parentNoteId?: number
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
    topics,
    noteTemplateId,
    parentNoteId
  }
  const contextStore = useContextStore()
  const apiPath: string = isPeerAdvisor(contextStore.currentUser) ? '/api/peer_advising/note/update' : '/api/notes/update'
  each(attachments, (attachment, index) => args[`attachment[${index}]`] = attachment)
  return utils.postMultipartFormData(apiPath, args).then(data => {
    const eventType = size(sids) > 1 ? 'notes-batch-published' : 'note-updated'
    contextStore.broadcast(eventType, data)
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

export function deleteNote(noteId: number) {
  $_track('delete')
  return axios.delete(`${utils.apiBaseUrl()}/api/notes/delete/${noteId}`).then(response => {
    useContextStore().broadcast('note-deleted', noteId)
    $_refreshMyDraftNoteCount()
    return response.data
  })
}

export function addAttachments(noteId: number, attachments: NoteAttachment[]): Promise<NoteEditSessionModel> {
  const data = {}
  each(attachments, (attachment, index) => data[`attachment[${index}]`] = attachment)
  return new Promise(resolve => {
    utils.postMultipartFormData(`/api/notes/${noteId}/attachments`, data).then(note => {
      useContextStore().broadcast('note-updated', note)
      resolve(note)
    })
  })
}

export function removeAttachment(note: Note, attachmentId: number) {
  const api: string = note.peerAdvisingDepartmentId ? `/api/peer_advising/note/${note.id}/attachment/${attachmentId}` : `/api/notes/${note.id}/attachment/${attachmentId}`
  return axios.delete(`${utils.apiBaseUrl()}${api}`).then(response => {
    const note = response.data
    useContextStore().broadcast('note-updated', note)
    return note
  })
}
