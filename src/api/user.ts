import {get, isNil} from 'lodash'
import axios from 'axios'
import utils from '@/api/api-utils'
import {useContextStore} from '@/stores/context'

export function getDepartments(excludeEmpty?: boolean) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/users/departments?excludeEmpty=${excludeEmpty}`)
    .then(response => response, () => null)
}

export function getAdminUsers(sortBy: string, sortDescending: boolean, ignoreDeleted?: boolean) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/users/admins`, {
      ignoreDeleted: isNil(ignoreDeleted) ? null : ignoreDeleted,
      sortBy,
      sortDescending
    })
    .then(response => response, () => null)
}

export function getUserProfile() {
  return axios
    .get(`${utils.apiBaseUrl()}/api/profile/my`)
    .then(response => {
      const user = response
      if (!get(user, 'isAuthenticated')) {
        useContextStore().broadcast('user-session-expired')
      }
      return user
    }, () => null)
}

export function getCalnetProfileByCsid(csid) {
  return axios.get(`${utils.apiBaseUrl()}/api/user/calnet_profile/by_csid/${csid}`).then(response => response, () => null)
}

export function getCalnetProfileByUserId(userId) {
  return axios.get(`${utils.apiBaseUrl()}/api/user/calnet_profile/by_user_id/${userId}`).then(response => response, () => null)
}

export function getCalnetProfileByUid(uid) {
  return axios.get(`${utils.apiBaseUrl()}/api/user/calnet_profile/by_uid/${uid}`).then(response => response, () => null)
}

export function getUserByUid(uid, ignoreDeleted?: boolean) {
  let url = `${utils.apiBaseUrl()}/api/user/by_uid/${uid}`
  if (!isNil(ignoreDeleted)) {
    url += `?ignoreDeleted=${ignoreDeleted}`
  }
  return axios.get(url).then(response => response, () => null)
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
    .then(response => response, () => null)
}

export function userAutocomplete(snippet: string) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/users/autocomplete`, {snippet: snippet})
    .then(response => response, () => null)
}

export function becomeUser(uid: string) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/auth/become_user`, {uid: uid})
    .then(response => response, () => null)
}

export function setDemoMode(demoMode: boolean) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/user/demo_mode`, {demoMode: demoMode})
    .then(() => {
      useContextStore().setDemoMode(demoMode)
    })
}

export function createOrUpdateUser(profile: any, memberships: any[], deleteAction: boolean) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/user/create_or_update`, {
      deleteAction,
      profile,
      memberships
    })
    .then(response => response)
}
