import axios from 'axios'
import utils from '@/api/api-utils'

export async function getAvailableDepartmentReports() {
  const url: string = `${utils.apiBaseUrl()}/api/reports/available_departments`
  return axios.get(url).then(response => response.data)
}

export async function getBoaNoteCountByMonth() {
  const url: string = `${utils.apiBaseUrl()}/api/reports/boa_notes/monthly_count`
  return axios.get(url).then(response => response.data)
}

export async function getNotesReport(deptCode: string) {
  const url: string = `${utils.apiBaseUrl()}/api/reports/notes/${deptCode}`
  return axios.get(url).then(response => response.data)
}

export async function getUsersReport(deptCode: string) {
  const url: string = `${utils.apiBaseUrl()}/api/reports/users/${deptCode}`
  return axios.get(url).then(response => response.data)
}
