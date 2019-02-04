import axios from 'axios';
import store from '@/store';

export function createCohort(
  name: string,
  filters: any[],
  studentCount: number
) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .post(`${apiBaseUrl}/api/cohort/create`, {
      name,
      filters,
      studentCount
    })
    .then(response => {
      const cohort = response.data;
      store.dispatch('cohort/addCohort', cohort);
      return cohort;
    }, () => null);
}

export function deleteCohort(id) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .delete(`${apiBaseUrl}/api/cohort/delete/${id}`, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(() => {
      store.commit('cohort/deleteCohort', id);
    }, () => null);
}

export function getCohort(
  id: number,
  includeStudents = true,
  orderBy = 'lastName'
) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(
      `${apiBaseUrl}/api/cohort/${id}?includeStudents=${includeStudents}&orderBy=${orderBy}`
    )
    .then(response => response.data, () => null);
}

export function getMyCohorts() {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/cohorts/my`)
    .then(response => response.data, () => null);
}

export function getStudentsPerFilters(
  filters: any[],
  orderBy: string,
  offset: number,
  limit: number
) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .post(`${apiBaseUrl}/api/cohort/get_students_per_filters`, {
      filters,
      orderBy,
      offset,
      limit
    })
    .then(response => response.data, () => null);
}

export function getStudentsWithAlerts(cohortId) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/cohort/${cohortId}/students_with_alerts`)
    .then(response => response.data, () => null);
}

export function getUsersWithCohorts() {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/cohorts/all`)
    .then(response => response.data, () => null);
}

export function saveCohort(
  id: number,
  name: string,
  filters?: any,
  studentCount?: number
) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .post(`${apiBaseUrl}/api/cohort/update`, {
      id,
      name,
      filters,
      studentCount
    })
    .then(response => {
      const cohort = response.data;
      store.dispatch('cohort/updateCohort', cohort);
      return cohort;
    }, () => null);
}
