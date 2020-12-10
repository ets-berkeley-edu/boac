import axios from 'axios'
import utils from '@/api/api-utils'

export function downloadAlertsCSV() {
  const url = `${utils.apiBaseUrl()}/api/reports/download_alerts_csv`
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

export function getAvailableDepartmentReports() {
  const url = `${utils.apiBaseUrl()}/api/reports/available_departments`
  return axios.get(url).then(response => response.data, () => null)
}
