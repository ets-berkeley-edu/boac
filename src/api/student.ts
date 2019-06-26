import axios from 'axios';
import utils from '@/api/api-utils';

export function dismissStudentAlert(alertId: string) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/alerts/${alertId}/dismiss`)
    .then(response => response.data, () => null);
}

export function getStudentByUid(uid: string) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/student/by_uid/${uid}`)
    .then(response => response.data, () => null);
}

export function getStudentBySid(sid: string) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/student/by_sid/${sid}`)
    .then(response => response.data, () => null);
}

export function validateSids(sids: string[]) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/students/validate_sids`, { sids: sids })
    .then(response => response.data, () => null);
}
