import axios from 'axios';
import store from '@/store';

const apiBaseUrl = store.getters['context/apiBaseUrl'];

export function dismissStudentAlert(alertId: string) {
  return axios
    .get(`${apiBaseUrl}/api/alerts/${alertId}/dismiss`)
    .then(response => response.data, () => null);
}

export function getStudentByUid(uid: string) {
  return axios
    .get(`${apiBaseUrl}/api/student/by_uid/${uid}`)
    .then(response => response.data, () => null);
}

export function getStudentBySid(sid: string) {
  return axios
    .get(`${apiBaseUrl}/api/student/by_sid/${sid}`)
    .then(response => response.data, () => null);
}

export function validateSids(sids: string[]) {
  return axios
    .post(`${apiBaseUrl}/api/students/validate_sids`, { sids: sids })
    .then(response => response.data, () => null);
}
