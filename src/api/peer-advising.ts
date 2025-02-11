import axios from 'axios'
import utils from '@/api/api-utils'

export function getPeerAdvisingDepartment(peerAdvisingDeptId: number) {
  const url: string = `${utils.apiBaseUrl()}/api/peer/department/${peerAdvisingDeptId}`
  return axios.get(url).then(response => response.data)
}
