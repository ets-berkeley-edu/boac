import axios from 'axios';
import store from '@/store';

export function getUsersWithCohorts() {
  return axios
    .get(`${store.state.apiBaseUrl}/api/filtered_cohorts/all`)
    .then(response => response.data, () => null);
}
