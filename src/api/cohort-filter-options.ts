import axios from 'axios'
import utils from '@/api/api-utils'

export function getCohortFilterOptions(domain: string, ownerUid: string | undefined, existingFilters: object[]) {
  const url: string = `${utils.apiBaseUrl()}/api/cohort_filter_options`
  return axios.post(url, {domain, existingFilters, ownerUid}).then(response => response.data)
}

export function translateToFilterOptions(domain: string, ownerUid: string, criteria: object) {
  const url: string = `${utils.apiBaseUrl()}/api/cohort_filter_options/translate`
  return axios.post(url, {criteria, domain, ownerUid}).then(response => response.data)
}
