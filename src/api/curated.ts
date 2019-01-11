import { event } from 'vue-analytics';
import axios from 'axios';
import store from '@/store';

export function addStudents(curatedGroup, sids) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .post(`${apiBaseUrl}/api/curated_group/students/add`, {
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

export function createCuratedGroup(name: string, sids: object) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .post(`${apiBaseUrl}/api/curated_group/create`, {
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
    .delete(`${apiBaseUrl}/api/curated_group/delete/${id}`, {
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

export function getCuratedGroup(id) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/curated_group/${id}`)
    .then(response => response.data, () => null);
}

export function getMyCuratedGroupIdsPerStudentId(sid: string) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/curated_groups/my/${sid}`)
    .then(response => response.data, () => null);
}

export function getMyCuratedGroups() {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/curated_groups/my`)
    .then(response => response.data, () => null);
}

export function removeFromCuratedGroup(groupId, sid) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .delete(`${apiBaseUrl}/api/curated_group/${groupId}/remove_student/${sid}`)
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

export function renameCuratedGroup(id, name) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  let group = {
    id: id,
    name: name
  };
  return axios
    .post(`${apiBaseUrl}/api/curated_group/rename`, group)
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

export function getStudentsWithAlerts(groupId) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/curated_group/${groupId}/students_with_alerts`)
    .then(response => response.data, () => null);
}
