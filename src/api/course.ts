import axios from 'axios'
import utils from '@/api/api-utils'

export function getSection(termId: number, sectionId: number, offset: number, limit: number, featured: string) {
  const params: string[] = []
  if (offset || limit) {
    params.push('offset=' + (offset || 0) + '&limit=' + (limit || 50))
  }
  if (featured) {
    params.push('featured=' + featured)
  }
  const url: string = `${utils.apiBaseUrl()}/api/section/${termId}/${sectionId}?${params.join('&')}`
  return axios.get(url).then(response => response.data)
}
