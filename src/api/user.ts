import axios from 'axios'
import {get, isNil} from 'lodash'
import utils from '@/api/api-utils'
import type {BoaUser} from '@/lib/types'
import {useContextStore} from '@/stores/context'

export function getDepartments(excludeEmpty?: boolean) {
  const url: string = `${utils.apiBaseUrl()}/api/users/departments?excludeEmpty=${excludeEmpty}`
  return axios.get(url).then(response => response.data)
}

export function getAdminUsers(sortBy: string, sortDescending: boolean, status: string) {
  const data = {
    sortBy,
    sortDescending,
    status
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

export function getCalnetProfileByUserId(userId: number) {
  const url: string = `${utils.apiBaseUrl()}/api/user/calnet_profile/by_user_id/${userId}`
  return axios.get(url).then(response => response.data)
}

export function getCalnetProfileByUid(uid: string) {
  const url: string = `${utils.apiBaseUrl()}/api/user/calnet_profile/by_uid/${uid}`
  return axios.get(url).then(response => response.data)
}

export function getPeerAdvisingUsers(
  peerAdvisingDepartmentId: number | undefined,
  role: string | undefined,
  sortBy: string,
  sortDescending: boolean,
  status: string
) {
  const data = {
    peerAdvisingDepartmentId,
    role,
    sortBy,
    sortDescending,
    status
  }
  return axios.post(`${utils.apiBaseUrl()}/api/users/peer_advising`, data)
    .then(response => response.data)
}

export function getUserByUid(uid: string, ignoreDeleted?: boolean) {
  let url = `${utils.apiBaseUrl()}/api/user/by_uid/${uid}`
  if (!isNil(ignoreDeleted)) {
    url += `?ignoreDeleted=${ignoreDeleted}`
  }
  return axios.get(url).then(response => response.data)
}

export function getUsers(
    deptCode: string,
    role: string,
    sortBy: string,
    sortDescending: boolean,
    status: string
  ) {
  const data = {
    deptCode,
    role,
    sortBy,
    sortDescending,
    status
  }
  return axios.post(`${utils.apiBaseUrl()}/api/users`, data).then(response => response.data)
}

export function userAutocomplete(snippet: string, abortController: AbortController) {
  const url: string = `${utils.apiBaseUrl()}/api/users/autocomplete`
  return axios.post(url, {snippet}, {signal: abortController.signal}).then(response => response.data)
}

export function becomeUser(uid: string) {
  const url: string = `${utils.apiBaseUrl()}/api/auth/become_user`
  return axios.post(url, {uid}).then(response => response.data)
}

export function setDemoMode(demoMode: boolean) {
  const url: string = `${utils.apiBaseUrl()}/api/user/demo_mode`
  return axios.post(url, {demoMode}).then(() => useContextStore().setDemoMode(demoMode))
}

export function createOrUpdateUser(user: BoaUser) {
  const url: string = `${utils.apiBaseUrl()}/api/user/create_or_update`
  return axios.post(url, {user}).then(response => response.data)
}
