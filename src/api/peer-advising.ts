import axios from 'axios'
import utils from '@/api/api-utils'

export function deletePeerAdvisor(peerAdvisingDeptId: number, userId: number) {
  const headers = {'Content-Type': 'application/json'}
  const url: string = `${utils.apiBaseUrl()}/api/peer/delete_peer_advisor/${peerAdvisingDeptId}/${userId}`
  return axios.delete(url, {headers})
}

export async function restorePeerAdvisor(peerAdvisingDeptId: number, userId: number) {
  const headers = {'Content-Type': 'application/json'}
  const url: string = `${utils.apiBaseUrl()}/api/peer/restore_peer_advisor/${peerAdvisingDeptId}/${userId}`
  return axios.get(url, {headers}).then(response => response.data)
}

export function getPeerAdvisingDepartment(peerAdvisingDeptId: number, includeDeleted?: boolean) {
  const url: string = `${utils.apiBaseUrl()}/api/peer/department/${peerAdvisingDeptId}?includeDeleted=${includeDeleted}`
  return axios.get(url).then(response => response.data)
}
