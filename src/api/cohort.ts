import axios from 'axios';
import store from '@/store';

export function getCohort(id: number, includeStudents = true) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/cohort/${id}?includeStudents=${includeStudents}`)
    .then(response => response.data, () => null);
}

export function getMyCohorts() {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/cohorts/my`)
    .then(response => response.data, () => null);
}

export function getUsersWithCohorts() {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/cohorts/all`)
    .then(response => response.data, () => null);
}
