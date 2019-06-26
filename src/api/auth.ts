import axios from 'axios';
import store from '@/store';
import utils from '@/api/api-utils';

export function devAuthLogIn(uid: string, password: string) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/auth/dev_auth_login`, {
      uid: uid,
      password: password
    })
    .then(response => {
      const user = response.data;
      if (user.isAuthenticated) {
        store.dispatch('user/registerUser', user);
        store.dispatch('context/initUserSession');
      }
      return user;
    }, error => error);
}

export function getCasLoginURL() {
  return axios
    .get(`${utils.apiBaseUrl()}/cas/login_url`)
    .then(response => response.data, () => null);
}

export function becomeUser(uid: string) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/auth/become_user`, { uid: uid })
    .then(response => response.data, () => null);
}

export function getCasLogoutUrl() {
  return axios
    .get(`${utils.apiBaseUrl()}/api/auth/logout`)
    .then(response => response.data, () => null);
}
