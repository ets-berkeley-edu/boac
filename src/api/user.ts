import _ from 'lodash';
import axios from 'axios';
import store from '@/store';
import utils from '@/api/api-utils';
import Vue from "vue";

export function getDepartments(excludeEmpty?: boolean) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/users/departments?excludeEmpty=${excludeEmpty}`)
    .then(response => response.data, () => null);
}

export function getAdminUsers(sortBy: string, sortDescending: boolean, ignoreDeleted?: boolean) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/users/admins`, {
      ignoreDeleted: _.isNil(ignoreDeleted) ? null : ignoreDeleted,
      sortBy,
      sortDescending
    })
    .then(response => response.data, () => null);
}

export function getUserProfile() {
  return axios
    .get(`${utils.apiBaseUrl()}/api/profile/my`)
    .then(response => response.data, () => null);
}

export function getCalnetProfileByCsid(csid) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/user/calnet_profile/by_csid/${csid}`)
    .then(response => response.data, () => null);
}

export function getCalnetProfileByUid(uid) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/user/calnet_profile/by_uid/${uid}`)
    .then(response => response.data, () => null);
}

export function getUserByUid(uid, ignoreDeleted?: boolean) {
  let url = `${utils.apiBaseUrl()}/api/user/by_uid/${uid}`;
  if (!_.isNil(ignoreDeleted)) {
    url += `?ignoreDeleted=${ignoreDeleted}`;
  }
  return axios.get(url).then(response => response.data, () => null);
}

export function getUsers(
    blocked: boolean,
    deleted: boolean,
    deptCode: string,
    role: string,
    sortBy: string,
    sortDescending: boolean
  ) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/users`, {
      blocked,
      deleted,
      deptCode,
      role,
      sortBy,
      sortDescending
    })
    .then(response => response.data, () => null);
}

export function userAutocomplete(snippet: string) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/users/autocomplete`, { snippet: snippet })
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
      if (uid === Vue.prototype.$currentUser.uid) {
        store.commit('currentUserExtras/setDropInStatus', {
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
    .post(`${utils.apiBaseUrl()}/api/user/demo_mode`, { demoMode: demoMode })
    .then(() => Vue.prototype.$currentUser.inDemoMode = demoMode);
}

export function createOrUpdateUser(profile: any, rolesPerDeptCode: any[], deleteAction: boolean) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/users/create_or_update`, {
      deleteAction,
      profile,
      rolesPerDeptCode
    })
    .then(response => response.data);
}
