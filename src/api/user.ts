import axios from 'axios';
import store from '@/store';
import utils from '@/api/api-utils';

export function getUserStatus() {
  return axios
    .get(`${utils.apiBaseUrl()}/api/user/status`)
    .then(response => response.data, () => null);
}

export function getUserProfile() {
  return axios
    .get(`${utils.apiBaseUrl()}/api/profile/my`)
    .then(response => response.data, () => null);
}

export function getUserByCsid(csid) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/user/by_csid/${csid}`)
    .then(response => response.data, () => null);
}

export function getUserByUid(uid) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/user/by_uid/${uid}`)
    .then(response => response.data, () => null);
}

export function getUsers(sortUsersBy: string) {
  let query = sortUsersBy ? `sortUsersBy=${sortUsersBy}` : '';
  return axios
    .get(`${utils.apiBaseUrl()}/api/users/all?${query}`)
    .then(response => response.data, () => null);
}

export function becomeUser(uid: string) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/auth/become_user`, { uid: uid })
    .then(response => response.data, () => null);
}

export function getDropInAdvisorsForDept(deptCode: string) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/users/drop_in_advisors/${deptCode}`)
    .then(response => response.data, () => null);
}

export function setDropInAvailability(deptCode: string, uid: string, available: boolean) {
  const action = available ? 'activate' : 'deactivate';
  return axios
    .post(`${utils.apiBaseUrl()}/api/user/${uid}/drop_in_status/${deptCode}/${action}`)
    .then(response => {
      if (uid === 'me') {
        store.dispatch('user/setDropInStatus', {
          deptCode: deptCode,
          available: available
        });
      } else {
        return response.data;
      }
    }, () => null);
}

export function setDemoMode(demoMode: boolean) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/user/demo_mode`, {
      demoMode: demoMode
    })
    .then(response => response.data, () => null)
    .then(() => {
      store.dispatch('user/setDemoMode', demoMode);
    });
}
