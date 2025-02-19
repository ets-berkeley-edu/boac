import axios from 'axios'
import utils from '@/api/api-utils'

export function getPeerAdvisingDepartment(peerAdvisingDeptId: number, includeDeleted?: boolean) {
  const url: string = `${utils.apiBaseUrl()}/api/peer/department/${peerAdvisingDeptId}?includeDeleted=${includeDeleted}`
  return axios.get(url).then(response => response.data)
}
