import axios from 'axios'
import utils from '@/api/api-utils'

export function getSection(termId, sectionId, offset, limit, featured) {
  let url = `${utils.apiBaseUrl()}/api/section/${termId}/${sectionId}`
  const params: string[] = []
  if (offset || limit) {
    params.push('offset=' + (offset || 0) + '&limit=' + (limit || 50))
  }
  if (featured) {
    params.push('featured=' + featured)
  }
  if (params.length) {
    url += '?' + params.join('&')
  }
  return axios.get(url).then(response => response.data, () => null)
}
