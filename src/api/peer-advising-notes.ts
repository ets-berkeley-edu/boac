import axios from 'axios'
import utils from '@/api/api-utils'
import {useContextStore} from '@/stores/context'

export async function getPeerAdvisorNotes(offset: number, limit: number, includeStudents?: boolean) {
  const params = `offset=${offset}&limit=${limit}&includeStudents=${includeStudents}`
  const url: string = `${utils.apiBaseUrl()}/api/peer_advisor/notes?${params}`
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
    useContextStore().broadcast('peer-advising-note-created', data)
    return data
  })
}
