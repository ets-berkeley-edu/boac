import axios from 'axios'
import utils from '@/api/api-utils'
import {useContextStore} from '@/stores/context'

export async function getPeerAdvisorNotes(peerAdvisingDeptId: number, userId: number) {
  const url: string = `${utils.apiBaseUrl()}/api/peer_advisor/notes/${peerAdvisingDeptId}/${userId}`
  return axios.get(url).then(response => response.data)
}

export async function getPeerAdvisingTopics() {
  const url: string = `${utils.apiBaseUrl()}/api/peer_advising/note_topics`
  return axios.get(url).then(response => response.data)
}

export function createPeerAdvisingNote(
    body: string,
    contactType: string | undefined,
    peerAdvisingDepartmentId: number,
    sid: string,
    subject: string,
    topics: string[]
) {
  const data = {
    body,
    contactType,
    peerAdvisingDepartmentId,
    sid,
    subject,
    topics
  }
  return axios.post(`${utils.apiBaseUrl()}/api/peer_advising/note/create`, data).then(response => {
    const data = response.data
    useContextStore().broadcast('note-created', data)
    return data
  })
}
