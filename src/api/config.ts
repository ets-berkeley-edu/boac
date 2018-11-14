import axios from 'axios';
import store from '@/store';

export function getAppConfig() {
  return axios
    .get(`${store.state.apiBaseUrl}/api/config`)
    .then(response => response.data, () => null);
}

export function setDemoMode(blur: boolean) {
  return axios
    .post(`${store.state.apiBaseUrl}/api/admin/demo_mode`, { blur: blur })
    .then(response => response.data, () => null);
}
