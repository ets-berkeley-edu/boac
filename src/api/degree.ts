import axios from 'axios'
import utils from '@/api/api-utils'
import Vue from 'vue'

const $_track = (action, label?) => Vue.prototype.$ga.degreeProgress(action, label)

export function addUnitRequirement(templateId: number, name: string, minUnits: number) {
  return axios.post(`${utils.apiBaseUrl()}/api/degree/${templateId}/unit_requirement`, {name, minUnits}).then(response => response.data, () => null)
}

export function copyCourse(categoryId, courseId) {
  const data = {
    categoryId,
    courseId
  }
  return axios.post(`${utils.apiBaseUrl()}/api/degree/course/copy`, data).then(response => response.data, () => null)
}

export function assignCourse(courseId: number, categoryId?: number, ignore?: boolean) {
  const data = {categoryId, ignore}
  return axios.post(`${utils.apiBaseUrl()}/api/degree/course/${courseId}/assign`, data).then(response => response.data, () => null)
}

export function cloneDegreeTemplate(templateId: number, name: string) {
  $_track('clone', 'Degree Template')
  return axios.post(`${utils.apiBaseUrl()}/api/degree/${templateId}/clone`, {name}).then(response => response.data, () => null)
}

export function createCourse(
  accentColor: string,
  degreeCheckId: number,
  grade: string,
  name: string,
  note: string,
  sid: string,
  unitRequirementIds: number[],
  units: number
) {
  const data = {
    accentColor,
    degreeCheckId,
    grade,
    name,
    note,
    sid,
    unitRequirementIds,
    units
  }
  return axios.post(`${utils.apiBaseUrl()}/api/degree/course/create`, data).then(response => response.data, () => null)
}

export function createDegreeCategory(
  categoryType: string,
  description: string,
  isSatisfiedByTransferCourse: boolean,
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
    isSatisfiedByTransferCourse,
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
  $_track('create', `${sids.length} Degree Checks`)
  return axios.post(`${utils.apiBaseUrl()}/api/degree/check/batch`, {sids, templateId}).then(response => response.data, () => null)
}

export function createDegreeCheck(sid: number, templateId: number) {
  $_track('create', 'Degree Check')
  return axios.post(`${utils.apiBaseUrl()}/api/degree/check/${sid}/create`, {templateId}).then(response => response.data, () => null)
}

export function createDegreeTemplate(name: string) {
  $_track('create', 'Degree Template')
  return axios.post(`${utils.apiBaseUrl()}/api/degree/create`, {name}).then(response => response.data, () => null)
}

export function deleteDegreeCategory(categoryId: number) {
  return axios.delete(`${utils.apiBaseUrl()}/api/degree/category/${categoryId}`)
}

export function deleteDegreeCourse(courseId: number) {
  return axios.delete(`${utils.apiBaseUrl()}/api/degree/course/${courseId}`)
}

export function deleteDegreeTemplate(templateId: number) {
  $_track('delete', 'Degree Template')
  return axios.delete(`${utils.apiBaseUrl()}/api/degree/${templateId}`)
}

export function deleteUnitRequirement(unitRequirementId: number) {
  return axios.delete(`${utils.apiBaseUrl()}/api/degree/unit_requirement/${unitRequirementId}`)
}

export function getDegreeChecks(uid: number) {
  return axios.get(`${utils.apiBaseUrl()}/api/degrees/student/${uid}`).then(response => response.data, () => null)
}

export function getDegreeTemplate(templateId: number) {
  $_track('view', 'Degree Template')
  return axios.get(`${utils.apiBaseUrl()}/api/degree/${templateId}`).then(response => response.data, () => null)
}

export function getDegreeTemplates() {
  $_track('view', 'Degree Templates')
  return axios.get(`${utils.apiBaseUrl()}/api/degree/templates`).then(response => response.data, () => null)
}

let $_getStudentsCancel = axios.CancelToken.source()

export function getStudents(templateId: number, sids: number[]) {
  if ($_getStudentsCancel) {
    $_getStudentsCancel.cancel()
 }
 $_getStudentsCancel = axios.CancelToken.source()
  return axios.post(
    `${utils.apiBaseUrl()}/api/degree/${templateId}/students`,
    {sids},
    {cancelToken: $_getStudentsCancel.token}
  ).then(response => response.data, () => null)
}

export function toggleCampusRequirement(categoryId: number, isSatisfied: boolean) {
  return axios.post(`${utils.apiBaseUrl()}/api/degree/category/${categoryId}/satisfy`, {isSatisfied}).then(response => response.data, () => null)
}

export function updateCourse(
  accentColor: string,
  courseId: number,
  grade: string,
  name: string,
  note: string,
  unitRequirementIds: number[],
  units: number
) {
  const data = {
    accentColor,
    grade,
    name,
    note,
    unitRequirementIds,
    units
  }
  return axios.post(`${utils.apiBaseUrl()}/api/degree/course/${courseId}/update`, data).then(response => response.data, () => null)
}

export function updateCourseRequirement(
  accentColor: string,
  categoryId: number,
  grade: string,
  isIgnored: boolean,
  isRecommended: boolean,
  note: string,
  unitsLower: number,
  unitsUpper: number
) {
  const data = {
    accentColor,
    grade,
    isIgnored,
    isRecommended,
    note,
    unitsLower,
    unitsUpper
  }
  return axios.post(`${utils.apiBaseUrl()}/api/degree/category/${categoryId}/recommend`, data).then(response => response.data, () => null)
}

export function updateCategory(
  categoryId: number,
  description: string,
  isSatisfiedByTransferCourse: boolean,
  name: string,
  parentCategoryId: number,
  unitRequirementIds: number[],
  unitsLower: number,
  unitsUpper: number
) {
  const data = {
    description,
    isSatisfiedByTransferCourse,
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
  $_track('update', 'Degree Template')
  return axios.post(`${utils.apiBaseUrl()}/api/degree/${templateId}/update`, {name}).then(response => response.data, () => null)
}

export function updateUnitRequirement(unitRequirementId: number, name: string, minUnits: number) {
  return axios.post(`${utils.apiBaseUrl()}/api/degree/unit_requirement/${unitRequirementId}/update`, {name, minUnits}).then(response => response.data, () => null)
}
