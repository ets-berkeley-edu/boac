import _ from 'lodash'
import axios from 'axios'
import moment from 'moment-timezone'
import utils from '@/api/api-utils'
import Vue from 'vue'

const $_track = action => Vue.prototype.$ga.curated(action)

const $_onCreate = group => {
  Vue.prototype.$currentUser.myCuratedGroups.push(group)
  Vue.prototype.$currentUser.myCuratedGroups = _.sortBy(Vue.prototype.$currentUser.myCuratedGroups, 'name')
  Vue.prototype.$eventHub.emit('my-curated-groups-updated', group.domain)
  $_track('create')
}

const $_onDelete = (domain, groupId) => {
  const indexOf = Vue.prototype.$currentUser.myCuratedGroups.findIndex(curatedGroup => curatedGroup.id === groupId)
  Vue.prototype.$currentUser.myCuratedGroups.splice(indexOf, 1)
  Vue.prototype.$eventHub.emit('my-curated-groups-updated', domain)
  $_track('delete')
}

const $_onUpdate = updatedGroup => {
  const groups = Vue.prototype.$currentUser.myCuratedGroups
  const group = groups.find(group => group.id === +updatedGroup.id)
  Object.assign(group, updatedGroup)
  Vue.prototype.$currentUser.myCuratedGroups = _.sortBy(groups, 'name')
  Vue.prototype.$eventHub.emit('my-curated-groups-updated', updatedGroup.domain)
  $_track('update')
}

export function addStudents(curatedGroupId: number, sids: string[], returnStudentProfiles?: boolean) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/curated_group/students/add`, {
      curatedGroupId: curatedGroupId,
      sids: sids,
      returnStudentProfiles: returnStudentProfiles
    })
    .then(response => {
      const group = response.data
      $_onUpdate(group)
      return group
    })
}

export function createCuratedGroup(domain: string, name: string, sids: string[]) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/curated_group/create`, {domain, name, sids})
    .then(function(response) {
      const group = response.data
      $_onCreate(group)
      return group
    })
}

export function deleteCuratedGroup(domain, id) {
  return axios
    .delete(`${utils.apiBaseUrl()}/api/curated_group/delete/${id}`, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(() => {
      $_onDelete(domain, id)
      $_track('delete')
    })
    .catch(error => error)
}

export function downloadCuratedGroupCsv(id: number, name: string, csvColumnsSelected: any[]) {
  $_track('download')
  const fileDownload = require('js-file-download')
  const now = moment().format('YYYY-MM-DD_HH-mm-ss')
  const termId = Vue.prototype.$currentUser.preferences.termId || Vue.prototype.$config.currentEnrollmentTermId
  const url = `${utils.apiBaseUrl()}/api/curated_group/${id}/download_csv`
  return axios.post(url, {csvColumnsSelected, termId})
    .then(response => fileDownload(response.data, `${name}-students-${now}.csv`), () => null)
}

export function getCuratedGroup(
  id: number,
  limit: number,
  offset: number,
  orderBy: string,
  termId: string
) {
  $_track('view')
  const url = `${utils.apiBaseUrl()}/api/curated_group/${id}?orderBy=${orderBy}&termId=${termId}&offset=${offset}&limit${limit}`
  return axios.get(url).then(response => response.data, () => null)
}

export function getUsersWithGroups() {
  return axios.get(`${utils.apiBaseUrl()}/api/curated_groups/all`).then(response => response.data, () => null)
}

export function removeFromCuratedGroup(groupId, sid) {
  return axios
    .delete(`${utils.apiBaseUrl()}/api/curated_group/${groupId}/remove_student/${sid}`)
    .then(response => {
      const group = response.data
      $_onUpdate(group)
      if (group.students) {
        group.students = _.remove(group.students, student => sid === (student.sid || student.csEmplId))
      }
      return group
    })
}

export function renameCuratedGroup(id, name) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/curated_group/rename`, {id: id, name: name})
    .then(response => {
      const group = response.data
      $_onUpdate(group)
      return group
    })
    .catch(error => error)
}

export function getStudentsWithAlerts(groupId) {
  const url = `${utils.apiBaseUrl()}/api/curated_group/${groupId}/students_with_alerts`
  return axios.get(url).then(response => response.data, () => null)
}
