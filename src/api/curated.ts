import axios from 'axios'
import moment from 'moment-timezone'
import store from '@/store'
import utils from '@/api/api-utils'
import Vue from 'vue'

export function addStudents(curatedGroupId: number, sids: string[], returnStudentProfiles?: boolean) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/curated_group/students/add`, {
      curatedGroupId: curatedGroupId,
      sids: sids,
      returnStudentProfiles: returnStudentProfiles
    })
    .then(response => {
      const group = response.data
      store.commit('currentUserExtras/curatedGroupUpdated', group)
      return group
    })
}

export function createCuratedGroup(name: string, sids: string[]) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/curated_group/create`, {
      name: name,
      sids: sids
    })
    .then(function(response) {
      const group = response.data
      store.commit('currentUserExtras/curatedGroupCreated', group)
      return group
    })
}

export function deleteCuratedGroup(id) {
  return axios
    .delete(`${utils.apiBaseUrl()}/api/curated_group/delete/${id}`, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(() => {
      store.commit('currentUserExtras/curatedGroupDeleted', id)
    })
    .then(() => Vue.prototype.$ga.curatedEvent(id, null, 'delete'))
    .catch(error => error)
}

export function downloadCuratedGroupCsv(id: number, name: string, csvColumnsSelected: any[]) {
  const fileDownload = require('js-file-download')
  const now = moment().format('YYYY-MM-DD_HH-mm-ss')
  return axios
    .post(`${utils.apiBaseUrl()}/api/curated_group/${id}/download_csv`, {csvColumnsSelected})
    .then(response => fileDownload(response.data, `${name}-students-${now}.csv`), () => null)
}

export function getCuratedGroup(
  id: number,
  orderBy: string,
  termId: string,
  offset: number,
  limit: number
) {
  const url = `${utils.apiBaseUrl()}/api/curated_group/${id}?orderBy=${orderBy}&termId=${termId}&offset=${offset}&limit${limit}`
  return axios
    .get(url)
    .then(response => response.data, () => null)
}

export function getMyCuratedGroupIdsPerStudentId(sid: string) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/curated_groups/my/${sid}`)
    .then(response => response.data, () => null)
}

export function getMyCuratedGroups() {
  return axios
    .get(`${utils.apiBaseUrl()}/api/curated_groups/my`)
    .then(response => response.data, () => null)
}

export function getUsersWithGroups() {
  return axios
    .get(`${utils.apiBaseUrl()}/api/curated_groups/all`)
    .then(response => response.data, () => null)
}

export function removeFromCuratedGroup(groupId, sid) {
  return axios
    .delete(`${utils.apiBaseUrl()}/api/curated_group/${groupId}/remove_student/${sid}`)
    .then(response => {
      const group = response.data
      store.commit('currentUserExtras/curatedGroupUpdated', group)
      Vue.prototype.$ga.curatedEvent(group.id, group.name, 'remove_student')
      return group
    })
}

export function renameCuratedGroup(id, name) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/curated_group/rename`, {id: id, name: name})
    .then(response => {
      const group = response.data
      store.commit('currentUserExtras/curatedGroupUpdated', group)
      Vue.prototype.$ga.curatedEvent(group.id, group.name, 'rename')
      return group
    })
    .catch(error => error)
}

export function getStudentsWithAlerts(groupId) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/curated_group/${groupId}/students_with_alerts`)
    .then(response => response.data, () => null)
}
