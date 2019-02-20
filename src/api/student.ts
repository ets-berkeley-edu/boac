import axios from 'axios';
import store from '@/store';
import { event } from 'vue-analytics';

export function dismissStudentAlert(alertId: string) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/alerts/${alertId}/dismiss`)
    .then(response => response.data, () => null);
}

export function getStudent(uid: string) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/student/${uid}`)
    .then(response => response.data, () => null);
}

export function search(
  phrase: string,
  includeCourses: boolean,
  orderBy: string,
  offset: number,
  limit: number
) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .post(`${apiBaseUrl}/api/search`, {
      searchPhrase: phrase,
      includeCourses: includeCourses,
      orderBy: orderBy || 'first_name',
      offset: offset || 0,
      limit: limit || 50
    })
    .then(response => {
      event('Students', 'search', phrase, store.getters['user/user'].uid);
      return response;
    })
    .then(response => response.data, () => null);
}
