import _ from 'lodash';
import axios from 'axios';
import store from '@/store';
import apiUtils from '@/api/api-utils';

export function markRead(noteId) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .post(`${apiBaseUrl}/api/notes/${noteId}/mark_read`)
    .then(response => response.data, () => null);
}

export function createNote(
    sids: any,
    subject: string,
    body: string,
    topics: string[],
    attachments: any[],
    cohortIds: number[],
    curatedGroupIds: number[]
) {
  const data = {sids, subject, body, topics, cohortIds, curatedGroupIds};
  _.each(attachments || [], (attachment, index) => data[`attachment[${index}]`] = attachment);
  return apiUtils.postMultipartFormData('/api/notes/create', data);
}

export function updateNote(
    noteId: number,
    subject: string,
    body: string,
    topics: string[],
    newAttachments: any[],
    deleteAttachmentIds: number[]
) {
  const data = {
    id: noteId,
    subject: subject,
    body: body,
    topics: topics,
    deleteAttachmentIds: deleteAttachmentIds || []
  };
  _.each(newAttachments || [], (attachment, index) => data[`attachment[${index}]`] = attachment);
  return apiUtils.postMultipartFormData('/api/notes/update', data);
}

export function deleteNote(noteId: number) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .delete(`${apiBaseUrl}/api/notes/delete/${noteId}`)
    .then(response => response.data);
}

export function getTopics() {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/notes/topics`)
    .then(response => response.data);
}

export function addAttachment(noteId: number, attachment: any) {
  const data = {
    'attachment[0]': attachment,
  };
  return apiUtils.postMultipartFormData(`/api/notes/${noteId}/attachment`, data);
}

export function removeAttachment(noteId: number, attachmentId: number) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .delete(`${apiBaseUrl}/api/notes/${noteId}/attachment/${attachmentId}`)
    .then(response => response.data);
}
