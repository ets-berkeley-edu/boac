import _ from 'lodash';
import axios from "axios";
import utils from "@/api/api-utils";
import store from "@/store";

export function getMyNoteTemplates() {
  return axios
    .get(`${utils.apiBaseUrl()}/api/note_templates/my`)
    .then(response => response.data, () => null);
}

export function getNoteTemplate(templateId: number) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/note_template/${templateId}`)
    .then(response => response.data, () => null);
}

export function createNoteTemplate(
    title: string,
    subject: string,
    body: string,
    topics: string[],
    attachments: any[]
) {
  const data = {title, subject, body, topics};
  _.each(attachments || [], (attachment, index) => data[`attachment[${index}]`] = attachment);
  return utils.postMultipartFormData('/api/note_template/create', data).then(template => {
    store.dispatch('noteEditSession/onCreateTemplate', template);
    store.dispatch('user/gaNoteTemplateEvent', {
      id: template.id,
      label: `Advisor ${store.getters['user/uid']} created a note template`,
      action: 'create'
    });
    return template;
  });
}

export function deleteNoteTemplate(templateId: number) {
  return axios
    .delete(`${utils.apiBaseUrl()}/api/note_template/delete/${templateId}`)
    .then(() => store.dispatch('noteEditSession/onDeleteTemplate', templateId));
}

export function renameNoteTemplate(noteTemplateId: number, title: string) {
  const data = {id: noteTemplateId, title: title};
  return axios.post(`${utils.apiBaseUrl()}/api/note_template/rename`, data).then(response => {
    const template = response.data;
    store.dispatch('noteEditSession/onUpdateTemplate', template);
    store.dispatch('user/gaNoteTemplateEvent', {
      id: noteTemplateId,
      name: `Advisor ${store.getters['user/uid']} renamed a note template`,
      action: 'update'
    });
    return template;
  });
}

export function updateNoteTemplate(
    noteTemplateId: number,
    subject: string,
    body: string,
    topics: string[],
    newAttachments: any[],
    deleteAttachmentIds: number[]
) {
  const data = {
    id: noteTemplateId,
    subject: subject,
    body: body,
    topics: topics,
    deleteAttachmentIds: deleteAttachmentIds || []
  };
  _.each(newAttachments || [], (attachment, index) => data[`attachment[${index}]`] = attachment);
  return utils.postMultipartFormData('/api/note_template/update', data).then(template => {
    store.dispatch('noteEditSession/onUpdateTemplate', template);
    store.dispatch('user/gaNoteTemplateEvent', {
      id: noteTemplateId,
      name: `Advisor ${store.getters['user/uid']} updated a note template`,
      action: 'update'
    });
    return template;
  });
}
