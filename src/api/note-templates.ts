import _ from 'lodash'
import axios from 'axios'
import utils from '@/api/api-utils'
import store from '@/store'
import Vue from 'vue'

const $_track = action => Vue.prototype.$ga.noteTemplate(action)

export function getMyNoteTemplates() {
  return axios
    .get(`${utils.apiBaseUrl()}/api/note_templates/my`)
    .then(response => response.data, () => null)
}

export function createNoteTemplate(noteId: number, title: string) {
  return axios.post(`${utils.apiBaseUrl()}/api/note_template/create`, {noteId, title}).then(template => {
    store.dispatch('noteEditSession/loadNoteTemplates')
    $_track('create')
    return template
  })
}

export function deleteNoteTemplate(templateId: number) {
  return axios
    .delete(`${utils.apiBaseUrl()}/api/note_template/delete/${templateId}`)
    .then(() => store.dispatch('noteEditSession/loadNoteTemplates', templateId))
}

export function renameNoteTemplate(noteTemplateId: number, title: string) {
  const data = {id: noteTemplateId, title: title}
  return axios.post(`${utils.apiBaseUrl()}/api/note_template/rename`, data).then(response => {
    const template = response.data
    store.dispatch('noteEditSession/onUpdateTemplate', template)
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
    store.dispatch('noteEditSession/onUpdateTemplate', template)
    $_track('update')
    return template
  })
}
