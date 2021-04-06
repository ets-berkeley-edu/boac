import axios from 'axios'
import utils from '@/api/api-utils'

export function createDegreeTemplate(degreeTemplateName: string) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/degree/new`, {
      degreeTemplateName: degreeTemplateName,
     })
    .then(function(response) {
      const degreeTemplate = response.data
      return degreeTemplate
    })
}
