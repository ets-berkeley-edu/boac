import axios from 'axios'
import utils from '@/api/api-utils'

export function addUnitRequirement(templateId: number, name: string, minUnits: number) {
  return axios.post(`${utils.apiBaseUrl()}/api/degree/${templateId}/unit_requirement`, {name, minUnits}).then(response => response.data, () => null)
}

export function assignCourse(categoryId: number, sectionId: number, sid: number, termId: number) {
  const data = {
    categoryId,
    sectionId,
    sid,
    termId
  }
  return axios.post(`${utils.apiBaseUrl()}/api/degree/course/assign`, data).then(response => response.data, () => null)
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
  templateId: number,
  unitRequirementIds: number[]
) {
  const data = {
    categoryType,
    courseUnits,
    description,
    name,
    parentCategoryId,
    position,
    templateId,
    unitRequirementIds
  }
  return axios.post(`${utils.apiBaseUrl()}/api/degree/category/create`, data).then(response => response.data, () => null)
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

export function getDegreeChecks(sid: number) {
  return axios.get(`${utils.apiBaseUrl()}/api/degrees/student/${sid}`).then(response => response.data, () => null)
}

export function getDegreeTemplate(templateId: number) {
  return axios.get(`${utils.apiBaseUrl()}/api/degree/${templateId}`).then(response => response.data, () => null)
}

export function getDegreeTemplates() {
  return axios.get(`${utils.apiBaseUrl()}/api/degree/templates`).then(response => response.data, () => null)
}

export function getUnassignedCourses(templateId) {
  return axios.get(`${utils.apiBaseUrl()}/api/degree/${templateId}/courses/unassigned`).then(response => response.data, () => null)
}

export function unassignCourse(sectionId: number, sid: number, termId: number) {
  const data = {
    sectionId,
    sid,
    termId
  }
  return axios.post(`${utils.apiBaseUrl()}/api/degree/course/unassign`, data).then(response => response.data, () => null)
}

export function updateCourse(
  sectionId: number,
  sid: string,
  termId: number,
  note: string,
  units: number
) {
  const data = {
    sectionId,
    sid,
    termId,
    note,
    units
  }
  return axios.post(`${utils.apiBaseUrl()}/api/degree/course/update`, data).then(response => response.data, () => null)
}

export function updateDegreeCategory(
  categoryId: number,
  courseUnits: number,
  description: string,
  name: string,
  parentCategoryId: number,
  unitRequirementIds: number[]
) {
  const data = {
    courseUnits,
    description,
    name,
    parentCategoryId,
    unitRequirementIds
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
