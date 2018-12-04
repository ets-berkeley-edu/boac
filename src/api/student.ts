import axios from 'axios';
import store from '@/store';

export function getStudentDetails(uid: string) {
  return axios
    .get(`${store.state.apiBaseUrl}/api/student/${uid}/analytics`)
    .then(response => response.data, () => null);
}

export function search(phrase: string) {
  return axios
    .post(`${store.state.apiBaseUrl}/api/students/search`, {
      searchPhrase: phrase
    })
    .then(response => response.data, () => null);
}
