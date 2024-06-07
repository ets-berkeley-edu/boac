import {replace} from 'lodash'
import axios from 'axios'
import utils from '@/api/api-utils'

export function getAvailableDepartmentReports() {
  const url: string = `${utils.apiBaseUrl()}/api/reports/available_departments`
  return axios.get(url).then(response => response.data)
}

export function downloadAlertsCSV(fromDate: string, toDate: string) {
  const fileDownload = require('js-file-download')
  const filename = `boa-alerts-${replace(fromDate, '/', '-')}-to-${replace(toDate, '/', '-')}`
  const url: string = `${utils.apiBaseUrl()}/api/reports/download_alerts_csv`
  const data = {fromDate, toDate}
  return axios.post(url, data).then(response => fileDownload(response.data, `${filename}.csv`))
}

export function getBoaNoteCountByMonth() {
  const url: string = `${utils.apiBaseUrl()}/api/reports/boa_notes/monthly_count`
  return axios.get(url).then(response => response.data)
}

export function getNotesReport(deptCode) {
  const url: string = `${utils.apiBaseUrl()}/api/reports/notes/${deptCode}`
  return axios.get(url).then(response => response.data)
}

export function getUsersReport(deptCode) {
  const url: string = `${utils.apiBaseUrl()}/api/reports/users/${deptCode}`
  return axios.get(url).then(response => response.data)
}
