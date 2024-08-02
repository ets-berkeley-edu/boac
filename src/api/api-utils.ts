import axios from 'axios'
import {each, get, isNil} from 'lodash'
import {useContextStore} from '@/stores/context'

export default {
  apiBaseUrl: () => get(useContextStore().config, 'apiBaseUrl'),
  postMultipartFormData: (path: string, data: object) => {
    const formData = new FormData()
    each(data, (value, key) => {
      if (!isNil(value)) {
        formData.append(key, value)
      }
    })
    const apiBaseUrl = get(useContextStore().config, 'apiBaseUrl')
    const config = {headers: {'Content-Type': 'multipart/form-data'}}
    return axios.post(`${apiBaseUrl}${path}`, formData, config)
      .then(response => response.data)
      .catch(error => {
        // eslint-disable-next-line no-console
        console.log(error)
        return error
      }
    )
  }
}
