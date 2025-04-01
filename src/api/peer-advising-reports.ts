import axios from 'axios'
import fileDownload from 'js-file-download'
import utils from '@/api/api-utils'
import type {PeerAdvisingDepartment} from '@/lib/types'
import {normalizeId} from '@/lib/utils'

export function downloadPeerAdvisingNotes(peerAdvisingDepartment: PeerAdvisingDepartment) {
  const url: string = `${utils.apiBaseUrl()}/api/peer_advising/${peerAdvisingDepartment.id}/notes/csv`
  return axios.post(url).then(response => {
    const csvFilename = `peer-advising-${normalizeId(peerAdvisingDepartment.name)}`
    const filename = utils.createDownloadFilename(csvFilename, 'csv')
    return fileDownload(response.data, filename)
  })
}

export function getPeerAdvisingHistoricalReport(peerAdvisingDepartmentId: number) {
  const url: string = `${utils.apiBaseUrl()}/api/peer_advising/${peerAdvisingDepartmentId}/report/historical`
  return axios.get(url).then(response => response.data)
}

export function getPeerAdvisingNotesReport(peerAdvisingDepartmentId: number) {
  const url: string = `${utils.apiBaseUrl()}/api/peer_advising/${peerAdvisingDepartmentId}/report/notes`
  return axios.get(url).then(response => response.data)
}
