import axios from 'axios';
import store from '@/store';

export function getAppConfig() {
  return axios
    .get(`${store.state.apiBaseUrl}/api/config`)
    .then(response => response.data, () => null);
}

export function setDemoMode(demoMode: boolean) {
  return axios
    .post(`${store.state.apiBaseUrl}/api/admin/demo_mode`, {
      demoMode: demoMode
    })
    .then(response => response.data, () => null)
    .then(() => {
      store.getters.user.inDemoMode = demoMode;
    });
}
