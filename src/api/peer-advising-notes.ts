import axios from 'axios'
import {each} from 'lodash'
import type {NoteEditSessionModel} from '@/lib/types'
import utils from '@/api/api-utils'
import {useContextStore} from '@/stores/context'

export async function addPeerAdvisingAttachments(noteId: number, attachments: object[]): Promise<NoteEditSessionModel> {
  const data = {}
  each(attachments, (attachment, index) => data[`attachment[${index}]`] = attachment)
  return new Promise(resolve => {
    utils.postMultipartFormData(`/api/peer_advisor/note/${noteId}/attachments`, data).then(note => {
      useContextStore().broadcast('note-updated', note)
      resolve(note)
    })
  })
}

export function getPeerAdvisingNotesAuthoredBy(peerAdvisingDepartmentId: number, uid: string) {
  const url: string = `${utils.apiBaseUrl()}/api/peer_advising/${peerAdvisingDepartmentId}/note_author/${uid}`
  return axios.get(url).then(response => response.data)
}

export async function getPeerAdvisorNotes(
  offset: number,
  limit: number,
  uid: string,
  includeStudents?: boolean
) {
  const params = `offset=${offset}&limit=${limit}&includeStudents=${includeStudents}`
  const url: string = `${utils.apiBaseUrl()}/api/peer_advisor/${uid}/notes?${params}`
  return axios.get(url).then(response => response.data)
}

export async function getPeerAdvisorNoteById(noteId: number) {
  const url: string = `${utils.apiBaseUrl()}/api/peer_advising/note/${noteId}`
  return axios.get(url).then(response => response.data)
}

export async function getPeerAdvisingTopics() {
  const url: string = `${utils.apiBaseUrl()}/api/peer_advising/note_topics`
  return axios.get(url).then(response => response.data)
}

export function createPeerAdvisingNote(
    body: string,
    contactType: string | undefined,
    peerAdvisingDepartmentId: number,
    sid: string,
    subject: string,
    topics: string[],
    noteTemplateId?: number
) {
  const data = {
    body,
    contactType,
    peerAdvisingDepartmentId,
    sid,
    subject,
    topics,
    noteTemplateId
  }
  return axios.post(`${utils.apiBaseUrl()}/api/peer_advising/note/create`, data).then(response => response.data)
}

export async function createPeerAdvisingNoteTemplate(peerAdvisingDeptId: number, body: string, title, topics: []) {
  const url: string = `${utils.apiBaseUrl()}/api/peer_advising/note_template/create`
  const noteTemplate = {
    peerAdvisingDeptId: peerAdvisingDeptId,
    body: body,
    topics: topics,
    title: title
  }
  return axios.post(url, noteTemplate).then(response => {
    return response.data
  })
}

export async function deletePeerAdvisingNoteTemplate(noteTemplateId: number) {
  const url: string = `${utils.apiBaseUrl()}/api/peer_advising/note_template/delete/${noteTemplateId}`
  const headers = {'Content-Type': 'application/json'}
  return axios.delete(url, {headers})
}

export function updatePeerAdvisingNote(
  id: number,
  body: string | undefined,
  contactType: string | undefined,
  subject: string | undefined,
  topics: string[],
  noteTemplateId?: number
) {
  const data = {
    id,
    body,
    contactType,
    subject,
    topics,
    noteTemplateId
  }
  return axios.post(`${utils.apiBaseUrl()}/api/peer_advising/note/update`, data).then(response => {
    const data = response.data
    useContextStore().broadcast('peer-advising-note-updated', data)
    return data
  })
}

export async function updatePeerAdvisingNoteTemplate(noteTemplateId: number, noteBody: string, title: string, topics: []) {
  const url: string = `${utils.apiBaseUrl()}/api/peer_advising/note_template/update`
  const noteTemplate = {
    id: noteTemplateId,
    body: noteBody,
    topics: topics,
    title: title
  }
  return axios.post(url, noteTemplate).then(response => {
    return response.data
  })
}
