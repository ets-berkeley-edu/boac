import axios from 'axios'
import moment from 'moment-timezone'
import utils from '@/api/api-utils'
import Vue from 'vue'

const $_track = (action, label?) => Vue.prototype.$ga.cohort(action, label)

const $_onCreate = cohort => {
  Vue.prototype.$currentUser.myCohorts.push(cohort)
  $_track('create')
}

const $_onDelete = cohortId => {
  const indexOf = Vue.prototype.$currentUser.myCohorts.findIndex(cohort => cohort.id === cohortId)
  Vue.prototype.$currentUser.myCohorts.splice(indexOf, 1)
  $_track('delete')
}

const $_onUpdate = updatedCohort => {
  const cohort = Vue.prototype.$currentUser.myCohorts.find(cohort => cohort.id === +updatedCohort.id)
  Object.assign(cohort, updatedCohort)
  $_track('update')
}

export function createCohort(
  domain: string,
  name: string,
  filters: any[]
) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/cohort/create`, {
      domain,
      name,
      filters
    })
    .then(response => {
      const cohort = response.data
      $_onCreate(cohort)
      return cohort
    }, () => null)
}

export function deleteCohort(id) {
  return axios
    .delete(`${utils.apiBaseUrl()}/api/cohort/delete/${id}`, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(() => $_onDelete(id), () => null)
}

export function downloadCohortCsv(cohortId: number, cohortName: string, csvColumnsSelected: any[]) {
  const fileDownload = require('js-file-download')
  const now = moment().format('YYYY-MM-DD_HH-mm-ss')
  const filename = cohortName ? `${cohortName}-students-${now}` : `students-${now}`
  $_track('download', filename)
  return axios
    .post(`${utils.apiBaseUrl()}/api/cohort/download_csv`, {
      cohortId,
      csvColumnsSelected
    })
    .then(response => fileDownload(response.data, `${filename}.csv`), () => null)
}

export function downloadCsv(domain: string, cohortName: string, filters: any[], csvColumnsSelected: any[]) {
  const fileDownload = require('js-file-download')
  const now = moment().format('YYYY-MM-DD_HH-mm-ss')
  const filename = cohortName ? `${cohortName}-students-${now}` : `students-${now}`
  $_track('download', filename)

  const url = `${utils.apiBaseUrl()}/api/cohort/download_csv_per_filters`
  return axios.post(url, {
    domain,
    filters,
    csvColumnsSelected
  })
  .then(response => fileDownload(response.data, `${filename}.csv`), () => null)
}

export function getCohort(
  id: number,
  includeStudents = true,
  limit: number = 50,
  offset: number = 0,
  orderBy = 'lastName',
  termId: string
) {
  $_track('view')
  const url = `${utils.apiBaseUrl()}/api/cohort/${id}?includeStudents=${includeStudents}&limit=${limit}&offset=${offset}&orderBy=${orderBy}&termId=${termId}`
  return axios.get(url).then(response => response.data, () => null)
}

export function getCohortEvents(id: number, offset: number, limit: number) {
  const url = `${utils.apiBaseUrl()}/api/cohort/${id}/events?offset=${offset}&limit=${limit}`
  return axios.get(url).then(response => response.data, () => null)
}

export function getCohortFilterOptions(domain: string, owner: string, existingFilters: any[]) {
  owner = owner || 'me'
  return axios
    .post(`${utils.apiBaseUrl()}/api/cohort/filter_options/${owner}`, {
      domain: domain,
      existingFilters: existingFilters
    })
    .then(response => response.data, () => null)
}

export function getStudentsPerFilters(
  domain: string,
  filters: any[],
  orderBy: string,
  termId: string,
  offset: number,
  limit: number
) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/cohort/get_students_per_filters`, {
      domain,
      filters,
      orderBy,
      termId,
      offset,
      limit
    })
    .then(response => response.data, () => null)
}

export function getStudentsWithAlerts(cohortId) {
  const url = `${utils.apiBaseUrl()}/api/cohort/${cohortId}/students_with_alerts`
  return axios.get(url).then(response => response.data, () => null)
}

export function getUsersWithCohorts() {
  return axios.get(`${utils.apiBaseUrl()}/api/cohorts/all`).then(response => response.data, () => null)
}

export function saveCohort(
  id: number,
  name: string,
  filters?: any
) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/cohort/update`, {
      id,
      name,
      filters
    })
    .then(response => {
      const cohort = response.data
      $_onUpdate(cohort)
      return cohort
    }, () => null)
}

export function translateToFilterOptions(domain: string, owner: string, criteria: any) {
  const data = {
    criteria,
    domain
  }
  const url = `${utils.apiBaseUrl()}/api/cohort/translate_to_filter_options/${owner}`
  return axios.post(url, data).then(response => response.data, () => null)
}
