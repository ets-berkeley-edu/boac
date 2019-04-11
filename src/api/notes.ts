import _ from 'lodash';
import axios from 'axios';
import store from '@/store';

export function markRead(noteId) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .post(`${apiBaseUrl}/api/notes/${noteId}/mark_read`)
    .then(response => response.data, () => null);
}

export function createNote(sid: any, subject: string, body: string, attachments: any[]) {
  const apiBaseUrl = store.getters['context/apiBaseUrl'];
  const formData = new FormData();
  formData.append('sid', sid.toString());
  formData.append('subject', subject);
  formData.append('body', body);
  _.each(attachments || [], (attachment, index) => formData.append(`files[${index}]`, attachment));
  return axios
    .post(
        `${apiBaseUrl}/api/notes/create`, formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
        )
    .then(response => response.data);
}

export function updateNote(noteId: number, subject: string, body: string) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .post(`${apiBaseUrl}/api/notes/update`, {
      id: noteId,
      subject: subject,
      body: body
    })
    .then(response => response.data);
}

export function deleteNote(noteId: number) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .delete(`${apiBaseUrl}/api/notes/delete/${noteId}`)
    .then(response => response.data);
}
