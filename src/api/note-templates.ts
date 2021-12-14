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

export function createNoteTemplate(
    attachments: any[],
    body: string,
    isPrivate: boolean,
    subject: string,
    title: string,
    topics: string[]
) {
  const data = {body, isPrivate, subject, title, topics}
  _.each(attachments || [], (attachment, index) => data[`attachment[${index}]`] = attachment)
  return utils.postMultipartFormData('/api/note_template/create', data).then(template => {
    store.dispatch('noteEditSession/onCreateTemplate', template)
    $_track('create')
    return template
  })
}

export function deleteNoteTemplate(templateId: number) {
  return axios
    .delete(`${utils.apiBaseUrl()}/api/note_template/delete/${templateId}`)
    .then(() => store.dispatch('noteEditSession/onDeleteTemplate', templateId))
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
