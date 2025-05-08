import axios from 'axios'
import fileDownload from 'js-file-download'
import ga from '@/lib/ga'
import utils from '@/api/api-utils'
import {useContextStore} from '@/stores/context'

const $_track = (action: string, label?: string) => ga.cohort(action, label)

export function downloadCohortCsv(cohortId: number, cohortName: string, csvColumnsSelected: string[]) {
  const contextStore = useContextStore()
  const termId = contextStore.currentUser.preferences.termId || contextStore.config.currentEnrollmentTermId
  const url: string = `${utils.apiBaseUrl()}/api/cohort_csv/download`
  return axios.post(url, {cohortId, csvColumnsSelected, termId}).then(response => {
    const filename = utils.createDownloadFilename(cohortName ? `${cohortName}-students` : 'students', 'csv')
    $_track('download', filename)
    return fileDownload(response.data, filename)
  })
}

export function downloadCsv(domain: string, cohortName: string, filters: object[], csvColumnsSelected: string[]) {
  const contextStore = useContextStore()
  const termId = contextStore.currentUser.preferences.termId || contextStore.config.currentEnrollmentTermId
  const url: string = `${utils.apiBaseUrl()}/api/cohort_csv/download_per_filters`
  return axios.post(url, {csvColumnsSelected, domain, filters, termId}).then(response => {
    $_track('download', `Cohort: ${cohortName || '[Not yet named]'}`)
    return fileDownload(response.data, utils.createDownloadFilename(cohortName || 'students', 'csv'))
  })
}
