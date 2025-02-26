import axios from 'axios'
import utils from '@/api/api-utils'

export async function getPeerAdvisorNotes(peerAdvisingDeptId: number, userId: number) {
  const url: string = `${utils.apiBaseUrl()}/api/peer_advisor/notes/${peerAdvisingDeptId}/${userId}`
  return axios.get(url).then(response => response.data)
}

export async function getPeerAdvisingTopics() {
  const url: string = `${utils.apiBaseUrl()}/api/peer_advising/note_topics`
  return axios.get(url).then(response => response.data)
}
