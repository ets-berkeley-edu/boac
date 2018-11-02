import axios from 'axios';
import store from '@/store';

export function getCasLoginURL() {
  return axios
    .get(`${store.state.apiBaseUrl}/cas/login_url`)
    .then(response => response.data, () => null);
}

export function getMyProfile() {
  return axios
    .get(`${store.state.apiBaseUrl}/api/profile/my`)
    .then(response => response.data, () => null);
}

export function getCasLogoutURL() {
  return axios
    .get(`${store.state.apiBaseUrl}/logout`)
    .then(response => response.data, () => null);
}
