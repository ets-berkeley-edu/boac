
import axios from 'axios'
import utils from '@/api/api-utils'

export function listUserTags() {
  const url: string = `${utils.apiBaseUrl()}/api/user_tag/list`
  return axios.get(url).then(response => response.data)
}
