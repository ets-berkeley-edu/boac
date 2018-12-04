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
