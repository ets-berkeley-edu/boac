import {each} from 'lodash'
import axios from 'axios'
import ga from '@/lib/ga'
import utils from '@/api/api-utils'
import {useNoteStore} from '@/stores/note-edit-session'

const $_refreshNoteEditSession = () => getMyNoteTemplates().then(data => useNoteStore().setNoteTemplates(data))

const $_track = action => ga.noteTemplate(action)

export function getMyNoteTemplates() {
  return axios.get(`${utils.apiBaseUrl()}/api/note_templates/my`).then(response => response.data)
}

export function createNoteTemplate(noteId: number, title: string) {
  const url: string = `${utils.apiBaseUrl()}/api/note_template/create`
  return axios.post(url, {noteId, title}).then(response => {
    $_refreshNoteEditSession()
    $_track('create')
    return response.data
  })
}

export function deleteNoteTemplate(templateId: number) {
  return axios.delete(`${utils.apiBaseUrl()}/api/note_template/delete/${templateId}`).then($_refreshNoteEditSession)
}

export function renameNoteTemplate(noteTemplateId: number, title: string) {
  return axios.post(`${utils.apiBaseUrl()}/api/note_template/rename`, {id: noteTemplateId, title}).then(response => {
    const data = response.data
    useNoteStore().onUpdateTemplate(data)
    $_track('update')
    return data
  })
}

export function updateNoteTemplate(
    body: string,
    deleteAttachmentIds: number[],
    isPrivate: boolean,
    newAttachments: any[],
    noteTemplateId: number,
    subject: string,
    topics: string[]
) {
  const args = {
    body,
    deleteAttachmentIds: deleteAttachmentIds || [],
    id: noteTemplateId,
    isPrivate,
    subject,
    topics,
  }
  each(newAttachments || [], (attachment, index) => args[`attachment[${index}]`] = attachment)
  return utils.postMultipartFormData('/api/note_template/update', args).then(data => {
    useNoteStore().onUpdateTemplate(data)
    $_track('update')
    return data
  })
}
