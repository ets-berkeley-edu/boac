import axios from 'axios'
import ga from '@/ga'
import utils from '@/api/api-utils'

const $_track = (action, label?) => ga.student(action, label)

export function getAdmitBySid(sid: string) {
  $_track('admit')
  const url = `${utils.apiBaseUrl()}/api/admit/by_sid/${sid}`
  return axios.get(url).then(response => response.data, () => null)
}

export function getAllAdmits(orderBy: string, limit: number, offset: number) {
  $_track('admits')
  const url = `${utils.apiBaseUrl()}/api/admits/all?offset=${offset}&limit=${limit}&orderBy=${orderBy}`
  return axios.get(url).then(response => response.data, () => null)
}
