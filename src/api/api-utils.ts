import {each, get, isNil} from 'lodash'
import axios from 'axios'
import {useContextStore} from '@/stores/context'

export default {
  apiBaseUrl: () => get(useContextStore().config, 'apiBaseUrl'),
  postMultipartFormData: (
    path: string,
    data: object
  ) => {
    const formData = new FormData()
    each(data, (value, key) => {
      if (!isNil(value)) {
        formData.append(key, value)
      }
    })
    const apiBaseUrl = get(useContextStore().config, 'apiBaseUrl')
    return axios
        .post(
            `${apiBaseUrl}${path}`,
            formData,
            {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            })
        .then(response => {
          return response
        })
        .catch(error => {
          console.log(error)
          return error
        }
      )
  }
}
