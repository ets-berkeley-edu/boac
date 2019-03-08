import axios from 'axios';
import store from '@/store';

export function markRead(noteId) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .post(`${apiBaseUrl}/api/notes/${noteId}/mark_read`)
    .then(response => response.data, () => null);
}

export function createNote(sid: object, subject: string, body: string) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .post(`${apiBaseUrl}/api/notes/create`, {
      sid: sid,
      subject: subject,
      body: body
    })
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
