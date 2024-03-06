import _ from 'lodash'
import axios from 'axios'
import ga from '@/lib/ga'
import utils from '@/api/api-utils'
import {useNoteStore} from '@/stores/note-edit-session'

const $_refreshNoteEditSession = () => {
  getMyNoteTemplates().then(templates => useNoteStore().setNoteTemplates(templates))
}

const $_track = action => ga.noteTemplate(action)

export function getMyNoteTemplates() {
  return axios
    .get(`${utils.apiBaseUrl()}/api/note_templates/my`)
    .then(response => response, () => null)
}

export function createNoteTemplate(noteId: number, title: string) {
  return axios.post(`${utils.apiBaseUrl()}/api/note_template/create`, {noteId, title}).then(template => {
    $_refreshNoteEditSession()
    $_track('create')
    return template
  })
}

export function deleteNoteTemplate(templateId: number) {
  return axios
    .delete(`${utils.apiBaseUrl()}/api/note_template/delete/${templateId}`)
    .then($_refreshNoteEditSession)
}

export function renameNoteTemplate(noteTemplateId: number, title: string) {
  const data = {id: noteTemplateId, title: title}
  return axios.post(`${utils.apiBaseUrl()}/api/note_template/rename`, data).then(template => {
    useNoteStore().onUpdateTemplate(template)
    $_track('update')
    return template
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
  const data = {
    body,
    deleteAttachmentIds: deleteAttachmentIds || [],
    id: noteTemplateId,
    isPrivate,
    subject,
    topics,
  }
  _.each(newAttachments || [], (attachment, index) => data[`attachment[${index}]`] = attachment)
  return utils.postMultipartFormData('/api/note_template/update', data).then(template => {
    useNoteStore().onUpdateTemplate(template)
    $_track('update')
    return template
  })
}
