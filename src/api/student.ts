import axios from 'axios'
import ga from '@/lib/ga'
import utils from '@/api/api-utils'

const $_track = (action, label?) => ga.student(action, label)

export function dismissStudentAlert(alertId: string) {
  $_track('dismiss alert')
  const url: string = `${utils.apiBaseUrl()}/api/alerts/${alertId}/dismiss`
  return axios.get(url).then(response => response.data)
}

export function getDistinctSids(sids: string[], cohortIds: number[], curatedGroupIds: number[]) {
  const url: string = `${utils.apiBaseUrl()}/api/students/distinct_sids`
  return axios.post(url, {sids, cohortIds, curatedGroupIds}).then(response => response.data)
}

export function getStudentByUid(uid: string, profileOnly?:boolean) {
  $_track('view')
  let url: string = `${utils.apiBaseUrl()}/api/student/by_uid/${uid}`
  url = profileOnly ? `${url}?profileOnly=true` : url
  return axios.get(url).then(response => response.data)
}

export function getStudentBySid(sid: string, profileOnly?:boolean) {
  let url: string = `${utils.apiBaseUrl()}/api/student/by_sid/${sid}`
  url = profileOnly ? `${url}?profileOnly=true` : url
  return axios.get(url).then(response => {
    const data = response.data
    $_track(data.uid)
    return data
  })
}

export function getStudentsBySids(sids: string[]) {
  const url: string = `${utils.apiBaseUrl()}/api/students/by_sids`
  return axios.post(url, {sids: sids}).then(response => response.data)
}

export function validateSids(domain: string, sids: string[]) {
  const url: string = `${utils.apiBaseUrl()}/api/students/validate_sids`
  return axios.post(url, {domain, sids}).then(response => response.data)
}

let $_findStudentsByNameOrSidCancel = axios.CancelToken.source()

export function findStudentsByNameOrSid(query: string, limit: number) {
  if ($_findStudentsByNameOrSidCancel) {
     $_findStudentsByNameOrSidCancel.cancel()
  }
  $_findStudentsByNameOrSidCancel = axios.CancelToken.source()
  const url: string = `${utils.apiBaseUrl()}/api/students/find_by_name_or_sid?q=${query}&limit=${limit}`
  const cancelToken = $_findStudentsByNameOrSidCancel.token
  return axios.get(url, {cancelToken}).then(response => response.data)
}
