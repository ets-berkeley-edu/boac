import axios from 'axios'
import utils from '@/api/api-utils'
import type {DepartmentMembershipRole} from '@/lib/types'

export function createPeerAdvisor(peerAdvisingDeptId: number, uid: string) {
  const url: string = `${utils.apiBaseUrl()}/api/peer_advising/create_peer_advisor`
  return axios.post(url, {peerAdvisingDeptId, uid})
    .then(response => response.data)
}

export function getBasicStudent(sid: string) {
  const url: string = `${utils.apiBaseUrl()}/api/peer_advising/student/${sid}`
  return axios.get(url).then(response => response.data)
}

export function getStudentEnrollments(sid: string) {
  const url: string = `${utils.apiBaseUrl()}/api/peer_advising/${sid}/enrollments`
  return axios.get(url).then(response => response.data)
}

export function deletePeerAdvisor(peerAdvisingDeptId: number, userId: number) {
  const headers = {'Content-Type': 'application/json'}
  const url: string = `${utils.apiBaseUrl()}/api/peer_advising/delete_peer_advisor/${peerAdvisingDeptId}/${userId}`
  return axios.delete(url, {headers})
}

export async function restorePeerAdvisor(peerAdvisingDeptId: number, userId: number) {
  const headers = {'Content-Type': 'application/json'}
  const url: string = `${utils.apiBaseUrl()}/api/peer_advising/restore_peer_advisor/${peerAdvisingDeptId}/${userId}`
  return axios.get(url, {headers}).then(response => response.data)
}

export async function getPeerAdvisingDepartment(
  peerAdvisingDeptId: number,
  roleType: DepartmentMembershipRole,
  includeDeleted?: boolean,
  includeNoteCounts?: boolean
) {
  const url: string = `${utils.apiBaseUrl()}/api/peer_advising/department/${peerAdvisingDeptId}/${roleType}?includeDeleted=${includeDeleted}&includeNoteCounts=${includeNoteCounts}`
  return axios.get(url).then(response => response.data)
}
