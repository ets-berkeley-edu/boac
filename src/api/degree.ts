import axios from 'axios'
import utils from '@/api/api-utils'

export function cloneDegreeTemplate(templateId: number, name: string) {
  return axios.post(`${utils.apiBaseUrl()}/api/degree/${templateId}/clone`, {name}).then(response => response.data, () => null)
}

export function createDegreeTemplate(name: string) {
  return axios.post(`${utils.apiBaseUrl()}/api/degree/create`, {name}).then(response => response.data, () => null)
}

export function deleteDegreeTemplate(templateId: number) {
  return axios.delete(`${utils.apiBaseUrl()}/api/degree/${templateId}`)
}

export function getDegreeTemplates() {
  return axios.get(`${utils.apiBaseUrl()}/api/degree/templates`).then(response => response.data, () => null)
}

export function updateDegreeTemplate(templateId: number, name: string) {
  return axios.post(`${utils.apiBaseUrl()}/api/degree/${templateId}/update`, {name}).then(response => response.data, () => null)
}
