import axios from 'axios';
import store from '@/store';

export function dismissStudentAlert(alertId: string) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/alerts/${alertId}/dismiss`)
    .then(response => response.data, () => null);
}

export function getStudentAlerts(sid: string) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/alerts/current/${sid}`)
    .then(response => response.data, () => null);
}

export function getStudentDetails(uid: string) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/student/${uid}/analytics`)
    .then(response => response.data, () => null);
}

export function search(
  phrase: string,
  includeCourses: boolean,
  isInactiveAsc: boolean,
  isInactiveCoe: boolean,
  orderBy: string,
  offset: number,
  limit: number
) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .post(`${apiBaseUrl}/api/students/search`, {
      searchPhrase: phrase,
      includeCourses: includeCourses,
      isInactiveAsc: isInactiveAsc,
      isInactiveCoe: isInactiveCoe,
      orderBy: orderBy || 'first_name',
      offset: offset || 0,
      limit: limit || 50
    })
    .then(response => response.data, () => null);
}
