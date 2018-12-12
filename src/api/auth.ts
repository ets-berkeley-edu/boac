import axios from 'axios';
import store from '@/store';

export function devAuthLogIn(uid: string, password: string) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .post(`${apiBaseUrl}/api/auth/dev_auth_login`, {
      uid: uid,
      password: password
    })
    .then(response => response.data, error => error);
}

export function getCasLoginURL() {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/cas/login_url`)
    .then(response => response.data, () => null);
}

export function becomeUser(uid: string) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .post(`${apiBaseUrl}/api/auth/become_user`, { uid: uid })
    .then(response => response.data, () => null);
}

export function getCasLogoutURL() {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/auth/logout`)
    .then(response => response.data, () => null);
}
