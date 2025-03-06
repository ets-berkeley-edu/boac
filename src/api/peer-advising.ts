import axios from 'axios'
import utils from '@/api/api-utils'
import type {DepartmentMembershipRole} from '@/lib/types'

export function createPeerAdvisor(peerAdvisingDeptId: number, uid: string) {
  const url: string = `${utils.apiBaseUrl()}/api/peer/create_peer_advisor`
  return axios.post(url, {peerAdvisingDeptId, uid})
    .then(response => response.data)
}

export function getStudentEnrollments(sid: string, termId?: number) {
  let url: string = `${utils.apiBaseUrl()}/api/peer_advising/${sid}/enrollments`
  if (termId) {
    url += `?termId=${termId}`
  }
  return axios.get(url).then(response => response.data)
}

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

export async function createPeerAdvisingNoteTemplate(peerAdvisingDeptId: number, body: string, title, topics: []) {
  const url: string = `${utils.apiBaseUrl()}/api/peer_advising/note_template/create`
  const noteTemplate = {
    peerAdvisingDeptId: peerAdvisingDeptId,
    body: body,
    topics: topics,
    title: title
  }
  return axios.post(url, noteTemplate).then(response => {
    return response.data
  })
}

export async function updatePeerAdvisingNoteTemplate(noteTemplateId: number, noteBody: string, title: string, topics: []) {
  const url: string = `${utils.apiBaseUrl()}/api/peer_advising/note_template/update`
  const noteTemplate = {
    id: noteTemplateId,
    body: noteBody,
    topics: topics,
    title: title
  }
  return axios.post(url, noteTemplate).then(response => {
    return response.data
  })
}

export async function deletePeerAdvisingNoteTemplate(noteTemplateId: number) {
  const url: string = `${utils.apiBaseUrl()}/api/peer_advising/note_template/delete/${noteTemplateId}`
  const headers = {'Content-Type': 'application/json'}
  return axios.delete(url, {headers})
}

export async function getPeerAdvisingDepartment(
  peerAdvisingDeptId: number,
  roleType: DepartmentMembershipRole,
  includeDeleted?: boolean,
  includeNoteCounts?: boolean
) {
  const url: string = `${utils.apiBaseUrl()}/api/peer/department/${peerAdvisingDeptId}/${roleType}?includeDeleted=${includeDeleted}&includeNoteCounts=${includeNoteCounts}`
  return axios.get(url).then(response => response.data)
}
