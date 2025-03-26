import axios from 'axios'
import utils from '@/api/api-utils'

export function getPeerAdvisingHistoricalReport(peerAdvisingDepartmentId: number) {
  const url: string = `${utils.apiBaseUrl()}/api/peer_advising/${peerAdvisingDepartmentId}/report/historical`
  return axios.get(url).then(response => response.data)
}

export function getPeerAdvisingNotesReport(peerAdvisingDepartmentId: number) {
  const url: string = `${utils.apiBaseUrl()}/api/peer_advising/${peerAdvisingDepartmentId}/report/notes`
  return axios.get(url).then(response => response.data)
}
