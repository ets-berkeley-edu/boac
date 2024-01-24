import _ from 'lodash'
import axios from 'axios'
import store from '@/store'
import utils from '@/api/api-utils'

export function getDepartments(excludeEmpty?: boolean) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/users/departments?excludeEmpty=${excludeEmpty}`)
    .then(response => response.data, () => null)
}

export function getAdminUsers(sortBy: string, sortDescending: boolean, ignoreDeleted?: boolean) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/users/admins`, {
      ignoreDeleted: _.isNil(ignoreDeleted) ? null : ignoreDeleted,
      sortBy,
      sortDescending
    })
    .then(response => response.data, () => null)
}

export function getUserProfile() {
  return axios
    .get(`${utils.apiBaseUrl()}/api/profile/my`)
    .then(response => {
      const user = response.data
      if (!user.isAuthenticated) {
        store.commit('context/broadcast', {eventType: 'user-session-expired'})
      }
      return user
    }, () => null)
}

export function getCalnetProfileByCsid(csid) {
  return axios.get(`${utils.apiBaseUrl()}/api/user/calnet_profile/by_csid/${csid}`).then(response => response.data, () => null)
}

export function getCalnetProfileByUserId(userId) {
  return axios.get(`${utils.apiBaseUrl()}/api/user/calnet_profile/by_user_id/${userId}`).then(response => response.data, () => null)
}

export function getCalnetProfileByUid(uid) {
  return axios.get(`${utils.apiBaseUrl()}/api/user/calnet_profile/by_uid/${uid}`).then(response => response.data, () => null)
}

export function getUserByUid(uid, ignoreDeleted?: boolean) {
  let url = `${utils.apiBaseUrl()}/api/user/by_uid/${uid}`
  if (!_.isNil(ignoreDeleted)) {
    url += `?ignoreDeleted=${ignoreDeleted}`
  }
  return axios.get(url).then(response => response.data, () => null)
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
    .then(response => response.data, () => null)
}

export function userAutocomplete(snippet: string) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/users/autocomplete`, {snippet: snippet})
    .then(response => response.data, () => null)
}

export function becomeUser(uid: string) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/auth/become_user`, {uid: uid})
    .then(response => response.data, () => null)
}

export function getDropInAdvisorsForDept(deptCode: string) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/users/drop_in_advisors/${deptCode}`)
    .then(response => response.data, () => null)
}

export function setDropInAvailability(deptCode: string, uid: string, available: boolean) {
  const availability = available ? 'available' : 'unavailable'
  return axios
    .post(`${utils.apiBaseUrl()}/api/user/${uid}/drop_in_advising/${deptCode}/${availability}`)
    .then(response => {
      if (uid === store.getters['context/currentUser'].uid) {
        store.commit('context/setDropInStatus', {
          available: _.get(response.data, 'available'),
          deptCode,
          status: _.get(response.data, 'status')
        })
      } else {
        return response.data
      }
    }, () => null)
}

export function setDropInStatus(deptCode: string, status?: string) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/user/drop_in_advising/${deptCode}/status`, {status: status || ''})
    .then(response => {
      store.commit('context/setDropInStatus', {
        available: _.get(response.data, 'available'),
        deptCode,
        status: _.get(response.data, 'status')
      })
    }, () => null)
}

export function getDropInSchedulers() {
  return axios
    .get(`${utils.apiBaseUrl()}/api/users/appointment_schedulers`)
    .then(response => response.data, () => null)
}

export function addDropInScheduler(deptCode: string, uid: string) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/users/appointment_schedulers/${deptCode}/add`, {uid: uid})
    .then(response => response.data, () => null)
}

export function removeDropInScheduler(deptCode: string, uid: string) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/users/appointment_schedulers/${deptCode}/remove`, {uid: uid})
    .then(response => response.data, () => null)
}

export function setDemoMode(demoMode: boolean) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/user/demo_mode`, {demoMode: demoMode})
    .then(() => store.commit('context/setDemoMode', demoMode))
}

export function createOrUpdateUser(profile: any, memberships: any[], deleteAction: boolean) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/user/create_or_update`, {
      deleteAction,
      profile,
      memberships
    })
    .then(response => response.data)
}

export function disableDropInAdvising(deptCode: string) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/user/drop_in_advising/${deptCode}/disable`)
    .then(() => store.commit('context/removeDropInStatus', deptCode.toUpperCase()))
    .catch(error => error)
  }

export function enableDropInAdvising(deptCode: string) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/user/drop_in_advising/${deptCode}/enable`)
    .then(response => store.commit('context/setDropInAdvisorStatus', response.data))
    .catch(error => error)
}
