import axios from 'axios'
import ga from '@/lib/ga'
import utils from '@/api/api-utils'

const $_track = (action: string, label?: string) => ga.student(action, label)

export function getAdmitBySid(sid: string) {
  $_track('admit')
  const url: string = `${utils.apiBaseUrl()}/api/admit/by_sid/${sid}`
  return axios.get(url).then(response => response.data)
}

export function getAllAdmits(orderBy: string, limit: number, offset: number) {
  $_track('admits')
  const url: string = `${utils.apiBaseUrl()}/api/admits/all?offset=${offset}&limit=${limit}&orderBy=${orderBy}`
  return axios.get(url).then(response => response.data)
}
