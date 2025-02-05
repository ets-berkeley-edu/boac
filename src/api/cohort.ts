import {Cohort} from '@/lib/cohort'
import axios from 'axios'
import fileDownload from 'js-file-download'
import ga from '@/lib/ga'
import utils from '@/api/api-utils'
import {useContextStore} from '@/stores/context'

const $_track = (action: string, label?: string) => ga.cohort(action, label)

const $_onCreate = (cohort: Cohort) => {
  useContextStore().addMyCohort(cohort)
  $_track('create')
}

const $_onDelete = (cohortId: number) => {
  useContextStore().removeMyCohort(cohortId)
  $_track('delete')
}

const $_onUpdate = (updatedCohort: Cohort) => {
  useContextStore().updateMyCohort(updatedCohort)
  $_track('update')
}

export function createCohort(
  domain: string,
  name: string,
  filters: object[]
) {
  const url: string = `${utils.apiBaseUrl()}/api/cohort/create`
  return axios.post(url, {domain, name, filters}).then(response => {
    const data = response.data
    $_onCreate(data)
    return data
  })
}

export function deleteCohort(id: number) {
  const url: string = `${utils.apiBaseUrl()}/api/cohort/delete/${id}`
  const headers = {'Content-Type': 'application/json'}
  return axios.delete(url, {headers}).then(() => $_onDelete(id))
}

export function downloadCohortCsv(cohortId: number, cohortName: string, csvColumnsSelected: string[]) {
  const contextStore = useContextStore()
  const termId = contextStore.currentUser.preferences.termId || contextStore.config.currentEnrollmentTermId
  const url: string = `${utils.apiBaseUrl()}/api/cohort/download_csv`
  return axios.post(url, {cohortId, csvColumnsSelected, termId}).then(response => {
    const filename = utils.createDownloadFilename(cohortName ? `${cohortName}-students` : 'students', 'csv')
    $_track('download', filename)
    return fileDownload(response.data, filename)
  })
}

export function downloadCsv(domain: string, cohortName: string, filters: object[], csvColumnsSelected: string[]) {
  const contextStore = useContextStore()
  const termId = contextStore.currentUser.preferences.termId || contextStore.config.currentEnrollmentTermId
  const url: string = `${utils.apiBaseUrl()}/api/cohort/download_csv_per_filters`
  return axios.post(url, {csvColumnsSelected, domain, filters, termId}).then(response => {
    $_track('download', `Cohort: ${cohortName || '[Not yet named]'}`)
    return fileDownload(response.data, utils.createDownloadFilename(cohortName || 'students', 'csv'))
  })
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
  const url: string = `${utils.apiBaseUrl()}/api/cohort/${id}?includeStudents=${includeStudents}&limit=${limit}&offset=${offset}&orderBy=${orderBy}&termId=${termId}`
  return axios.get(url).then(response => response.data)
}

export function getCohortEvents(id: number, offset: number, limit: number) {
  const url: string = `${utils.apiBaseUrl()}/api/cohort/${id}/events?offset=${offset}&limit=${limit}`
  return axios.get(url).then(response => response.data)
}

export function getCohortFilterOptions(domain: string, owner: string | undefined, existingFilters: object[]) {
  owner = owner || 'me'
  const url: string = `${utils.apiBaseUrl()}/api/cohort/filter_options/${owner}`
  return axios.post(url, {domain, existingFilters}).then(response => response.data)
}

export function getStudentsPerFilters(
  domain: string,
  filters: object[],
  orderBy: string,
  termId: string,
  offset: number,
  limit: number
) {
  const url: string = `${utils.apiBaseUrl()}/api/cohort/get_students_per_filters`
  const data = {domain, filters, orderBy, termId, offset, limit}
  return axios.post(url, data).then(response => response.data)
}

export function getStudentsWithAlerts(cohortId: number) {
  const url: string = `${utils.apiBaseUrl()}/api/cohort/${cohortId}/students_with_alerts`
  return axios.get(url).then(response => response.data)
}

export function getUsersWithCohortsByDeptCode(deptCode: string) {
  const url: string = `${utils.apiBaseUrl()}/api/cohorts/by_dept_code/${deptCode}`
  return axios.get(url).then(response => response.data)
}

export function saveCohort(
  id: number,
  name: string,
  filters?: object[]
) {
  const url: string = `${utils.apiBaseUrl()}/api/cohort/update`
  return axios.post(url, {id, filters, name}).then(response => {
    const data = response.data
    $_onUpdate(data)
    return data
  })
}

export function translateToFilterOptions(domain: string, owner: string, criteria: object) {
  const url: string = `${utils.apiBaseUrl()}/api/cohort/translate_to_filter_options/${owner}`
  return axios.post(url, {criteria, domain}).then(response => response.data)
}
