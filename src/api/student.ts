import axios from 'axios';
import store from '@/store';

export function getStudentDetails(uid: string) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/student/${uid}/analytics`)
    .then(response => response.data, () => null);
}

export function search(phrase: string) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .post(`${apiBaseUrl}/api/students/search`, {
      searchPhrase: phrase
    })
    .then(response => response.data, () => null);
}
