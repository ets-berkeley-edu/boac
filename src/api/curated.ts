import { event } from 'vue-analytics';
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
      store.dispatch('curated/createCuratedGroup', group);
      return group;
    })
    .then(group => {
      event('Curated Cohort', 'create', group.name, group.id, {
        userId: store.getters['user/user'].uid
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
      store.commit('curated/deleteCuratedGroup', id);
    })
    .then(() => {
      event('Curated Cohort', 'delete', null, id, {
        userId: store.getters['user/user'].uid
      });
    })
    .catch(error => error);
}

export function renameCuratedGroup(id, name) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  let group = {
    id: id,
    name: name
  };
  return axios
    .post(`${apiBaseUrl}/api/curated_cohort/rename`, group)
    .then(() => {
      store.commit('curated/updateCuratedGroup', group);
    })
    .then(() => {
      event('Curated Cohort', 'rename', group.name, group.id, {
        userId: store.getters['user/user'].uid
      });
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
      store.dispatch('curated/updateCuratedGroup', group);
      return group;
    })
    .then(group => {
      event('Curated Cohort', 'add_students', group.name, group.id, {
        userId: store.getters['user/user'].uid
      });
    });
}

export function removeFromCuratedGroup(groupId, sid) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .delete(`${apiBaseUrl}/api/curated_cohort/${groupId}/remove_student/${sid}`)
    .then(response => {
      const group = response.data;
      store.dispatch('curated/updateCuratedGroup', group);
      return group;
    })
    .then(group => {
      event('Curated Cohort', 'remove_student', group.name, group.id, {
        userId: store.getters['user/user'].uid
      });
    });
}
