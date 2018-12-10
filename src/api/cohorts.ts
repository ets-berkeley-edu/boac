import axios from 'axios';
import store from '@/store';

export function getUsersWithCohorts() {
  return axios
    .get(`${store.state.apiBaseUrl}/api/filtered_cohorts/all`)
    .then(response => response.data, () => null);
}

export function getCuratedGroup(id) {
  return axios
    .get(`${store.state.apiBaseUrl}/api/curated_cohort/${id}`)
    .then(response => response.data, () => null);
}

export function createCuratedGroup(name: string, sids: object) {
  return axios
    .post(`${store.state.apiBaseUrl}/api/curated_cohort/create`, {
      name: name,
      sids: sids
    })
    .then(function(response) {
      const group = response.data;
      store.commit('createdCuratedGroup', group);
      // TODO: implement GA tracking (BOAC-1506)
      // googleAnalyticsService.track('Curated Cohort', 'create', cohort.name, cohort.id);
      return group;
    });
}

export function deleteCuratedGroup(id) {
  return axios
    .delete(`${store.state.apiBaseUrl}/api/curated_cohort/delete/${id}`, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(() => {
      // TODO: implement GA tracking (BOAC-1495)
      // googleAnalyticsService.track('Curated Cohort', 'delete', null, id);
    })
    .catch(error => error);
}

export function renameCuratedGroup(id, name) {
  return axios
    .post(`${store.state.apiBaseUrl}/api/curated_cohort/rename`, {
      id: id,
      name: name
    })
    .then(response => {
      // TODO: implement GA tracking (BOAC-1495)
      // googleAnalyticsService.track('Curated Cohort', 'rename', cohort.name, cohort.id);
      return response.data;
    })
    .catch(error => error);
}

export function addStudents(curatedGroup, sids) {
  return axios
    .post(`${store.state.apiBaseUrl}/api/curated_cohort/students/add`, {
      curatedCohortId: curatedGroup.id,
      sids: sids
    })
    .then(response => {
      const group = response.data;
      store.commit('updateCuratedGroup', group);
      // TODO: implement GA tracking (BOAC-1506)
      // googleAnalyticsService.track('Curated Cohort', 'add_students', cohort.name, cohort.id);
      return group;
    });
}

export function removeFromCuratedGroup(groupId, sid) {
  return axios
    .delete(
      `${
        store.state.apiBaseUrl
      }/api/curated_cohort/${groupId}/remove_student/${sid}`
    )
    .then(response => {
      const group = response.data;
      store.commit('updateCuratedGroup', group);
      // TODO: implement GA tracking (BOAC-1506)
      // googleAnalyticsService.track('Curated Cohort', 'remove_student', cohort.name, cohort.id);
      return group;
    });
}
