import _ from 'lodash'
import axios from 'axios'
import {useContextStore} from '@/stores/context'

export default {
  apiBaseUrl: () => _.get(useContextStore().config, 'apiBaseUrl'),
  postMultipartFormData: (
    path: string,
    data: object
  ) => {
    const formData = new FormData()
    _.each(data, (value, key) => {
      if (!_.isNil(value)) {
        formData.append(key, value)
      }
    })
    const apiBaseUrl = _.get(useContextStore().config, 'apiBaseUrl')
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
