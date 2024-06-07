import {get, isNil} from 'lodash'
import axios from 'axios'
import utils from '@/api/api-utils'
import {useContextStore} from '@/stores/context'

export function getDepartments(excludeEmpty?: boolean) {
  const url: string = `${utils.apiBaseUrl()}/api/users/departments?excludeEmpty=${excludeEmpty}`
  return axios.get(url).then(response => response.data)
}

export function getAdminUsers(sortBy: string, sortDescending: boolean, ignoreDeleted?: boolean) {
  const data = {
    ignoreDeleted: isNil(ignoreDeleted) ? null : ignoreDeleted,
    sortBy,
    sortDescending
  }
  return axios.post(`${utils.apiBaseUrl()}/api/users/admins`, data).then(response => response.data)
}

export function getUserProfile() {
  return axios.get(`${utils.apiBaseUrl()}/api/profile/my`).then(response => {
    const data = response.data
    if (!get(data, 'isAuthenticated')) {
      useContextStore().broadcast('user-session-expired')
    }
    return data
  })
}

export function getCalnetProfileByCsid(csid) {
  const url: string = `${utils.apiBaseUrl()}/api/user/calnet_profile/by_csid/${csid}`
  return axios.get(url).then(response => response.data)
}

export function getCalnetProfileByUserId(userId) {
  const url: string = `${utils.apiBaseUrl()}/api/user/calnet_profile/by_user_id/${userId}`
  return axios.get(url).then(response => response.data)
}

export function getCalnetProfileByUid(uid) {
  const url: string = `${utils.apiBaseUrl()}/api/user/calnet_profile/by_uid/${uid}`
  return axios.get(url).then(response => response.data)
}

export function getUserByUid(uid, ignoreDeleted?: boolean) {
  let url = `${utils.apiBaseUrl()}/api/user/by_uid/${uid}`
  if (!isNil(ignoreDeleted)) {
    url += `?ignoreDeleted=${ignoreDeleted}`
  }
  return axios.get(url).then(response => response.data)
}

export function getUsers(
    blocked: boolean,
    deleted: boolean,
    deptCode: string,
    role: string,
    sortBy: string,
    sortDescending: boolean
  ) {
  const data = {
    blocked,
    deleted,
    deptCode,
    role,
    sortBy,
    sortDescending
  }
  return axios.post(`${utils.apiBaseUrl()}/api/users`, data).then(response => response.data)
}

export function userAutocomplete(snippet: string) {
  const url: string = `${utils.apiBaseUrl()}/api/users/autocomplete`
  return axios.post(url, {snippet}).then(response => response.data)
}

export function becomeUser(uid: string) {
  const url: string = `${utils.apiBaseUrl()}/api/auth/become_user`
  return axios.post(url, {uid}).then(response => response.data)
}

export function setDemoMode(demoMode: boolean) {
  const url: string = `${utils.apiBaseUrl()}/api/user/demo_mode`
  return axios.post(url, {demoMode}).then(() => useContextStore().setDemoMode(demoMode))
}

export function createOrUpdateUser(profile: any, memberships: any[], deleteAction: boolean) {
  const url: string = `${utils.apiBaseUrl()}/api/user/create_or_update`
  return axios.post(url, {deleteAction, profile, memberships}).then(response => response.data)
}
