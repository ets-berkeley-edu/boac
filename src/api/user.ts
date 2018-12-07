import axios from 'axios';
import store from '@/store';

export function devAuthLogIn(uid: string, password: string) {
  return axios
    .post(`${store.state.apiBaseUrl}/api/auth/dev_auth_login`, {
      uid: uid,
      password: password
    })
    .then(response => {
      let status = response.data;
      return status;
    }, error => error);
}

export function getCasLoginURL() {
  return axios
    .get(`${store.state.apiBaseUrl}/cas/login_url`)
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

export function getCasLogoutURL() {
  return axios
    .get(`${store.state.apiBaseUrl}/api/auth/logout`)
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
