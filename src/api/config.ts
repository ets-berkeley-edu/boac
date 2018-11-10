import axios from 'axios';
import store from '@/store';

export function getAppConfig() {
  return axios
    .get(`${store.state.apiBaseUrl}/api/config`)
    .then(response => response.data, () => null);
}
