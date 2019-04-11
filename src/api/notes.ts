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

export function createNote(sid: any, subject: string, body: string, attachments: any[]) {
  const data = {
    sid: sid.toString(),
    subject: subject,
    body: body
  };
  _.each(attachments || [], (attachment, index) => data[`files[${index}]`] = attachment);
  return apiUtils.postMultipartFormData('/api/notes/create', data);
}

export function updateNote(
    noteId: number,
    subject: string,
    body: string,
    attachments: any[],
    deleteAttachmentIds: number[]
) {
  const data = {
    id: noteId,
    subject: subject,
    body: body,
    deleteAttachmentIds: deleteAttachmentIds || []
  };
  _.each(attachments || [], (attachment, index) => data[`files[${index}]`] = attachment);
  return apiUtils.postMultipartFormData('/api/notes/update', data);
}

export function deleteNote(noteId: number) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .delete(`${apiBaseUrl}/api/notes/delete/${noteId}`)
    .then(response => response.data);
}
