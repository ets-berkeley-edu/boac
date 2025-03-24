import axios from 'axios'
import utils from '@/api/api-utils'

export function getPeerAdvisingNotesReport(peerAdvisingDepartmentId: number) {
  const url: string = `${utils.apiBaseUrl()}/api/peer_advising/${peerAdvisingDepartmentId}/report/notes`
  return axios.get(url).then(response => response.data)
}
