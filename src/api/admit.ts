import axios from 'axios'
import utils from '@/api/api-utils'

export function getAdmitBySid(sid: string) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/admit/by_sid/${sid}`)
    .then(response => response.data, () => null)
}

export function getAllAdmits(orderBy: string, limit: number, offset: number) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/admits/all?offset=${offset}&limit=${limit}&orderBy=${orderBy}`)
    .then(response => response.data, () => null)
}
