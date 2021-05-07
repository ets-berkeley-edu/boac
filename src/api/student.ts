import axios from 'axios'
import utils from '@/api/api-utils'

export function dismissStudentAlert(alertId: string) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/alerts/${alertId}/dismiss`)
    .then(response => response.data, () => null)
}

export function getDistinctSids(sids: string[], cohortIds: number[], curatedGroupIds: number[]) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/students/distinct_sids`, {sids, cohortIds, curatedGroupIds})
    .then(response => response.data, () => null)
}

export function getStudentByUid(uid: string, profileOnly?:boolean) {
  let url = `${utils.apiBaseUrl()}/api/student/by_uid/${uid}`
  url = profileOnly ? `${url}?profileOnly=true` : url
  return axios.get(url).then(response => response.data, () => null)
}

export function getStudentBySid(sid: string, profileOnly?:boolean) {
  let url = `${utils.apiBaseUrl()}/api/student/by_sid/${sid}`
  url = profileOnly ? `${url}?profileOnly=true` : url
  return axios.get(url).then(response => response.data, () => null)
}

export function getStudentsBySids(sids: string[]) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/students/by_sids`, {sids: sids})
    .then(response => response.data, () => null)
}

export function validateSids(sids: string[]) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/students/validate_sids`, {sids: sids})
    .then(response => response.data, () => null)
}

let $_findStudentsByNameOrSidCancel = axios.CancelToken.source()

export function findStudentsByNameOrSid(query: string, limit: number) {
  if ($_findStudentsByNameOrSidCancel) {
     $_findStudentsByNameOrSidCancel.cancel()
  }
  $_findStudentsByNameOrSidCancel = axios.CancelToken.source()
  return axios
    .get(
      `${utils.apiBaseUrl()}/api/students/find_by_name_or_sid?q=${query}&limit=${limit}`,
      {cancelToken: $_findStudentsByNameOrSidCancel.token}
    ).then(response => response.data, () => [])
}
