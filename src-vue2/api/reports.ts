import _ from 'lodash'
import axios from 'axios'
import utils from '@/api/api-utils'

export function getAvailableDepartmentReports() {
  const url = `${utils.apiBaseUrl()}/api/reports/available_departments`
  return axios.get(url).then(response => response.data, () => null)
}

export function downloadAlertsCSV(fromDate: string, toDate: string) {
  const fileDownload = require('js-file-download')
  const filename = `boa-alerts-${_.replace(fromDate, '/', '-')}-to-${_.replace(toDate, '/', '-')}`
  return axios
    .post(`${utils.apiBaseUrl()}/api/reports/download_alerts_csv`, {
      fromDate,
      toDate
    })
    .then(response => fileDownload(response.data, `${filename}.csv`), () => null)
}

export function getBoaNoteCountByMonth() {
  const url = `${utils.apiBaseUrl()}/api/reports/boa_notes/monthly_count`
  return axios.get(url).then(response => response.data, () => null)
}

export function getNotesReport(deptCode) {
  const url = `${utils.apiBaseUrl()}/api/reports/notes/${deptCode}`
  return axios.get(url).then(response => response.data, () => null)
}

export function getUsersReport(deptCode) {
  const url = `${utils.apiBaseUrl()}/api/reports/users/${deptCode}`
  return axios.get(url).then(response => response.data, () => null)
}
