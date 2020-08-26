import _ from 'lodash'
import axios from 'axios'
import Vue from 'vue'

export default {
  apiBaseUrl: () => Vue.prototype.$config.apiBaseUrl,
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
    const apiBaseUrl = Vue.prototype.$config.apiBaseUrl
    return axios
        .post(
            `${apiBaseUrl}${path}`,
            formData,
            {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            })
        .then(response => response.data)
  }
}
