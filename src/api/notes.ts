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

export function wasRead(noteId) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .post(`${apiBaseUrl}/api/notes/was_read/${noteId}`)
    .then(response => response.data, () => null);
}
