import axios from 'axios';
import store from '@/store';

export function getNotes(sid) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/notes/student/${sid}`)
    .then(response => response.data, () => null);
}

export function getNote(noteId) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/notes/${noteId}`)
    .then(response => response.data, () => null);
}

export function markRead(noteId) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .post(`${apiBaseUrl}/api/notes/${noteId}/mark_read`)
    .then(response => response.data, () => null);
}
