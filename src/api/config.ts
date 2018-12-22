import axios from 'axios';
import store from '@/store';

export function getConfig() {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/config`)
    .then(response => response.data, () => null);
}
