import axios from 'axios';
import store from '@/store';

export function devAuthLogIn(uid: string, password: string) {
  return axios
    .post(`${store.state.apiBaseUrl}/devauth/login`, {
      uid: uid,
      password: password
    })
    .then(response => response.data, () => null);
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
    .post(`${store.state.apiBaseUrl}/api/admin/become_user`, { uid: uid })
    .then(response => response.data, () => null);
}

export function getCasLogoutURL() {
  return axios
    .get(`${store.state.apiBaseUrl}/logout`)
    .then(response => response.data, () => null);
}
