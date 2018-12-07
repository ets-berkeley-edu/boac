import axios from 'axios';
import store from '@/store';

export function getUserStatus() {
  return axios
    .get(`${store.state.apiBaseUrl}/api/user/status`)
    .then(response => response.data, () => null);
}

export function getUserProfile() {
  return axios
    .get(`${store.state.apiBaseUrl}/api/profile/my`)
    .then(response => response.data, () => null);
}

export function getAuthorizedUserGroups() {
  return axios
    .get(`${store.state.apiBaseUrl}/api/profiles/authorized_user_groups`)
    .then(response => response.data, () => null);
}

export function becomeUser(uid: string) {
  return axios
    .post(`${store.state.apiBaseUrl}/api/auth/become_user`, { uid: uid })
    .then(response => response.data, () => null);
}

export function setDemoMode(demoMode: boolean) {
  return axios
    .post(`${store.state.apiBaseUrl}/api/user/demo_mode`, {
      demoMode: demoMode
    })
    .then(response => response.data, () => null)
    .then(() => {
      store.getters.user.inDemoMode = demoMode;
    });
}
