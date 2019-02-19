import axios from 'axios';
import store from '@/store';

export function getUserStatus() {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/user/status`)
    .then(response => response.data, () => null);
}

export function getUserProfile() {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/profile/my?excludeCohorts=true`)
    .then(response => response.data, () => null);
}

export function getCalnetUserByCsid(csid) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/profile/calnet_for_csid/${csid}`)
    .then(response => response.data, () => null);
}

export function getUserGroups(sortUsersBy: string) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  let query = sortUsersBy ? `sortUsersBy=${sortUsersBy}` : '';
  return axios
    .get(`${apiBaseUrl}/api/users/authorized_groups?${query}`)
    .then(response => response.data, () => null);
}

export function becomeUser(uid: string) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .post(`${apiBaseUrl}/api/auth/become_user`, { uid: uid })
    .then(response => response.data, () => null);
}

export function setDemoMode(demoMode: boolean) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .post(`${apiBaseUrl}/api/user/demo_mode`, {
      demoMode: demoMode
    })
    .then(response => response.data, () => null)
    .then(() => {
      store.dispatch('user/setDemoMode', demoMode);
    });
}
