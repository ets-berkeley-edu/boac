import {DateTime} from 'luxon'
import {get, isNil} from 'lodash'
import axios from 'axios'
import fileDownload from 'js-file-download'
import type {BoaUser} from '@/lib/types'
import utils from '@/api/api-utils'
import {useContextStore} from '@/stores/context'

const $_getCsvFilename = (prefix: string): string => {
  const now: string = DateTime.now().toFormat('yyyy-MM-dd_HH-mm-ss')
  return `${prefix.replaceAll('_', '-')}-${now}.csv`
}

export function getDepartments() {
  const url: string = `${utils.apiBaseUrl()}/api/users/departments`
  return axios.get(url).then(response => response.data)
}

export function getAdminUsers(
  sortBy: string,
  sortDescending: boolean,
  status: string,
  csvFilenamePrefix?: string
) {
  const isCsvDownloadRequest = !isNil(csvFilenamePrefix)
  const data = {
    isCsvDownloadRequest,
    sortBy,
    sortDescending,
    status
  }
  const url = `${utils.apiBaseUrl()}/api/users/admins`
  return axios.post(url, data).then(response => {
    return isCsvDownloadRequest ? fileDownload(response.data, $_getCsvFilename(csvFilenamePrefix)) : response.data
  })
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

export async function getPeerAdvisingUsers(
  peerAdvisingDepartmentId: number | undefined,
  roleType: string | undefined,
  sortBy: string,
  sortDescending: boolean,
  status: string,
  csvFilenamePrefix?: string
) {
  const isCsvDownloadRequest = !isNil(csvFilenamePrefix)
  const data = {
    isCsvDownloadRequest,
    peerAdvisingDepartmentId,
    roleType,
    sortBy,
    sortDescending,
    status
  }
  return axios.post(`${utils.apiBaseUrl()}/api/users/peer_advising`, data).then(response => {
    return isCsvDownloadRequest ? fileDownload(response.data, $_getCsvFilename(csvFilenamePrefix)) : response.data
  })
}

export function getUserByUid(uid: string, includeDeleted: boolean) {
  const url = `${utils.apiBaseUrl()}/api/user/by_uid/${uid}?includeDeleted=${includeDeleted}`
  return axios.get(url).then(response => response.data)
}

export function getUsers(
  deptCode: string,
  role: string,
  sortBy: string,
  sortDescending: boolean,
  status: string,
  csvFilenamePrefix?: string
) {
  const isCsvDownloadRequest = !isNil(csvFilenamePrefix)
  const data = {
    deptCode,
    isCsvDownloadRequest,
    role,
    sortBy,
    sortDescending,
    status
  }
  const url = `${utils.apiBaseUrl()}/api/users`
  return axios.post(url, data).then(response => {
    return isCsvDownloadRequest ? fileDownload(response.data, $_getCsvFilename(csvFilenamePrefix)) : response.data
  })
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
