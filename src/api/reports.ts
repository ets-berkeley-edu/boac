import axios from 'axios';
import utils from '@/api/api-utils';

export function getNotesReport(deptCode) {
  let url = `${utils.apiBaseUrl()}/api/reports/notes/${deptCode}`;
  return axios.get(url).then(response => response.data, () => null);
}

export function getUsersReport(deptCode) {
  let url = `${utils.apiBaseUrl()}/api/reports/users/${deptCode}`;
  return axios.get(url).then(response => response.data, () => null);
}

export function getAvailableDepartmentReports() {
  let url = `${utils.apiBaseUrl()}/api/reports/available_departments`;
  return axios.get(url).then(response => response.data, () => null);
}
