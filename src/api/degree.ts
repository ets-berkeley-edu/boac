import axios from 'axios'
import utils from '@/api/api-utils'

export function addUnitRequirement(templateId: number, name: string, minUnits: number) {
  return axios.post(`${utils.apiBaseUrl()}/api/degree/${templateId}/unit_requirement`, {name, minUnits}).then(response => response.data, () => null)
}

export function copyCourseAndAssign(categoryId, sectionId, sid, termId) {
  const data = {
    categoryId,
    sectionId,
    sid,
    termId,
  }
  return axios.post(`${utils.apiBaseUrl()}/api/degree/course/copy`, data).then(response => response.data, () => null)
}

export function assignCourse(courseId: number, categoryId?: number) {
  return axios.post(`${utils.apiBaseUrl()}/api/degree/course/${courseId}/assign`, {categoryId}).then(response => response.data, () => null)
}

export function cloneDegreeTemplate(templateId: number, name: string) {
  return axios.post(`${utils.apiBaseUrl()}/api/degree/${templateId}/clone`, {name}).then(response => response.data, () => null)
}

export function createDegreeCategory(
  categoryType: string,
  description: string,
  name: string,
  parentCategoryId: number,
  position: number,
  templateId: number,
  unitRequirementIds: number[],
  unitsLower: number,
  unitsUpper: number
) {
  const data = {
    categoryType,
    description,
    name,
    parentCategoryId,
    position,
    templateId,
    unitRequirementIds,
    unitsLower,
    unitsUpper
  }
  return axios.post(`${utils.apiBaseUrl()}/api/degree/category/create`, data).then(response => response.data, () => null)
}

export function createBatchDegreeCheck(sids: number[], templateId: number) {
  return axios.post(`${utils.apiBaseUrl()}/api/degree/check/batch`, {sids, templateId}).then(response => response.data, () => null)
}

export function createDegreeCheck(sid: number, templateId: number) {
  return axios.post(`${utils.apiBaseUrl()}/api/degree/check/${sid}/create`, {templateId}).then(response => response.data, () => null)
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

export function deleteUnitRequirement(unitRequirementId: number) {
  return axios.delete(`${utils.apiBaseUrl()}/api/degree/unit_requirement/${unitRequirementId}`)
}

export function getDegreeChecks(uid: number) {
  return axios.get(`${utils.apiBaseUrl()}/api/degrees/student/${uid}`).then(response => response.data, () => null)
}

export function getDegreeTemplate(templateId: number) {
  return axios.get(`${utils.apiBaseUrl()}/api/degree/${templateId}`).then(response => response.data, () => null)
}

export function getDegreeTemplates() {
  return axios.get(`${utils.apiBaseUrl()}/api/degree/templates`).then(response => response.data, () => null)
}

export function updateCourse(courseId: number, note: string, unitRequirementIds: number[], units: number) {
  const data = {note, unitRequirementIds, units}
  return axios.post(`${utils.apiBaseUrl()}/api/degree/course/${courseId}/update`, data).then(response => response.data, () => null)
}

export function updateCategory(
  categoryId: number,
  description: string,
  name: string,
  parentCategoryId: number,
  unitRequirementIds: number[],
  unitsLower: number,
  unitsUpper: number
) {
  const data = {
    description,
    name,
    parentCategoryId,
    unitRequirementIds,
    unitsLower,
    unitsUpper
  }
  return axios.post(`${utils.apiBaseUrl()}/api/degree/category/${categoryId}/update`, data).then(response => response.data, () => null)
}

export function updateDegreeNote(templateId: number, body: string) {
  return axios.post(`${utils.apiBaseUrl()}/api/degree/${templateId}/note`, {body}).then(response => response.data, () => null)
}

export function updateDegreeTemplate(templateId: number, name: string) {
  return axios.post(`${utils.apiBaseUrl()}/api/degree/${templateId}/update`, {name}).then(response => response.data, () => null)
}

export function updateUnitRequirement(unitRequirementId: number, name: string, minUnits: number) {
  return axios.post(`${utils.apiBaseUrl()}/api/degree/unit_requirement/${unitRequirementId}/update`, {name, minUnits}).then(response => response.data, () => null)
}
