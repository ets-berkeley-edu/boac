import axios from 'axios'
import utils from '@/api/api-utils'

export function addUnitRequirement(templateId: number, name: string, minUnits: number) {
  return axios.post(`${utils.apiBaseUrl()}/api/degree/${templateId}/unit_requirement`, {name, minUnits}).then(response => response.data, () => null)
}

export function cloneDegreeTemplate(templateId: number, name: string) {
  return axios.post(`${utils.apiBaseUrl()}/api/degree/${templateId}/clone`, {name}).then(response => response.data, () => null)
}

export function createDegreeCategory(
  categoryType: string,
  courseUnits: number,
  description: string,
  name: string,
  parentCategoryId: number,
  position: number,
  templateId: number
) {
  const data = {
    categoryType,
    courseUnits,
    description,
    name,
    parentCategoryId,
    position,
    templateId
  }
  return axios.post(`${utils.apiBaseUrl()}/api/degree/category/create`, data).then(response => response.data, () => null)
}

export function createDegreeTemplate(name: string) {
  return axios.post(`${utils.apiBaseUrl()}/api/degree/create`, {name}).then(response => response.data, () => null)
}

export function deleteDegreeCategory(categoryId: number) {
  return axios.delete(`${utils.apiBaseUrl()}/api/degree/category/${categoryId}`)
}

export function deleteDegreeTemplate(templateId: number) {
  return axios.delete(`${utils.apiBaseUrl()}/api/degree/${templateId}`)
}

export function getDegreeTemplate(templateId: number) {
  return axios.get(`${utils.apiBaseUrl()}/api/degree/${templateId}`).then(response => response.data, () => null)
}

export function getDegreeTemplates() {
  return axios.get(`${utils.apiBaseUrl()}/api/degree/templates`).then(response => response.data, () => null)
}

export function updateDegreeTemplate(templateId: number, name: string) {
  return axios.post(`${utils.apiBaseUrl()}/api/degree/${templateId}/update`, {name}).then(response => response.data, () => null)
}

export function updateUnitRequirement(unitRequirementId: number, name: string, minUnits: number) {
  return axios.post(`${utils.apiBaseUrl()}/api/degree/unit_requirement/${unitRequirementId}/update`, {name, minUnits}).then(response => response.data, () => null)
}
