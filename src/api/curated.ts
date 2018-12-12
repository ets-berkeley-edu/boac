import axios from 'axios';
import store from '@/store';

export function getMyCuratedGroups() {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/curated_groups/my`)
    .then(response => response.data, () => null);
}

export function getCuratedGroup(id) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/curated_cohort/${id}`)
    .then(response => response.data, () => null);
}

export function createCuratedGroup(name: string, sids: object) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .post(`${apiBaseUrl}/api/curated_cohort/create`, {
      name: name,
      sids: sids
    })
    .then(function(response) {
      const group = response.data;
      store.dispatch('curated/createdCuratedGroup', group).then(() => {
        // TODO: implement GA tracking (BOAC-1506)
        // googleAnalyticsService.track('Curated Cohort', 'create', cohort.name, cohort.id);
        return group;
      });
    });
}

export function deleteCuratedGroup(id) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .delete(`${apiBaseUrl}/api/curated_cohort/delete/${id}`, {
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
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .post(`${apiBaseUrl}/api/curated_cohort/rename`, {
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
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .post(`${apiBaseUrl}/api/curated_cohort/students/add`, {
      curatedCohortId: curatedGroup.id,
      sids: sids
    })
    .then(response => {
      const group = response.data;
      store.dispatch('curated/updateCuratedGroup', group).then(() => {
        // TODO: implement GA tracking (BOAC-1506)
        // googleAnalyticsService.track('Curated Cohort', 'add_students', cohort.name, cohort.id);
        return group;
      });
    });
}

export function removeFromCuratedGroup(groupId, sid) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .delete(`${apiBaseUrl}/api/curated_cohort/${groupId}/remove_student/${sid}`)
    .then(response => {
      const group = response.data;
      store.dispatch('curated/updateCuratedGroup', group).then(() => {
        // TODO: implement GA tracking (BOAC-1506)
        // googleAnalyticsService.track('Curated Cohort', 'remove_student', cohort.name, cohort.id);
        return group;
      });
    });
}
