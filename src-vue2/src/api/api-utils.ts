import _ from 'lodash'
import axios from 'axios'
import store from '@/store'

export default {
  apiBaseUrl: () => store.getters['context/config'].apiBaseUrl,
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
    const apiBaseUrl = store.getters['context/config'].apiBaseUrl
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
          return response.data
        })
        .catch(error => {
          console.log(error)
          return error
        }
      )
  }
}
