import axios from 'axios'
import utils from '@/api/api-utils'

export function createDegreeTemplate(name: string) {
  return axios.post(`${utils.apiBaseUrl()}/api/degree/create`, {name})
}
