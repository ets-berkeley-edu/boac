import axios from 'axios'
import ga from '@/lib/ga'
import utils from '@/api/api-utils'

const $_track = (action, label?) => ga.degreeProgress(action, label)

export function addUnitRequirement(templateId: number, name: string, minUnits: number) {
  const url: string = `${utils.apiBaseUrl()}/api/degree/${templateId}/unit_requirement`
  return axios.post(url, {minUnits, name}).then(response => response.data)
}

export function copyCourse(courseId: number, parentCategoryId?: number) {
  const url: string = `${utils.apiBaseUrl()}/api/degree/course/copy`
  return axios.post(url, {courseId, parentCategoryId}).then(response => response.data)
}

export function assignCourse(courseId: number, categoryId?: number | null, ignore?: boolean) {
  const url: string = `${utils.apiBaseUrl()}/api/degree/course/${courseId}/assign`
  return axios.post(url, {categoryId, ignore}).then(response => response.data)
}

export function cloneDegreeTemplate(templateId: number, name: string) {
  $_track('clone', 'Degree Template')
  const url: string = `${utils.apiBaseUrl()}/api/degree/${templateId}/clone`
  return axios.post(url, {name}).then(response => response.data)
}

export function createCourse(
  accentColor: string,
  degreeCheckId: number,
  grade: string,
  name: string,
  note: string,
  parentCategoryId: number,
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
    parentCategoryId,
    sid,
    unitRequirementIds,
    units
  }
  const url: string = `${utils.apiBaseUrl()}/api/degree/course/create`
  return axios.post(url, data).then(response => response.data)
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
  const url: string = `${utils.apiBaseUrl()}/api/degree/category/create`
  return axios.post(url, data).then(response => response.data)
}

export function createBatchDegreeCheck(sids: number[], templateId: number) {
  $_track('create', `${sids.length} Degree Checks`)
  const url: string = `${utils.apiBaseUrl()}/api/degree/check/batch`
  return axios.post(url, {sids, templateId}).then(response => response.data)
}

export function createDegreeCheck(sid: number, templateId: number) {
  $_track('create', 'Degree Check')
  const url: string = `${utils.apiBaseUrl()}/api/degree/check/${sid}/create`
  return axios.post(url, {templateId}).then(response => response.data)
}

export function createDegreeTemplate(name: string) {
  $_track('create', 'Degree Template')
  const url: string = `${utils.apiBaseUrl()}/api/degree/create`
  return axios.post(url, {name}).then(response => response.data)
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
  const url: string = `${utils.apiBaseUrl()}/api/degrees/student/${uid}`
  return axios.get(url).then(response => response.data)
}

export function getDegreeTemplate(templateId: number) {
  $_track('view', 'Degree Template')
  const url: string = `${utils.apiBaseUrl()}/api/degree/${templateId}`
  return axios.get(url).then(response => response.data)
}

export function getDegreeTemplates() {
  $_track('view', 'Degree Templates')
  return axios.get(`${utils.apiBaseUrl()}/api/degree/templates`).then(response => response.data)
}

let $_getStudentsCancel = axios.CancelToken.source()

export function getStudents(templateId: number, sids: number[]) {
  if ($_getStudentsCancel) {
    $_getStudentsCancel.cancel()
 }
 $_getStudentsCancel = axios.CancelToken.source()
  const url: string = `${utils.apiBaseUrl()}/api/degree/${templateId}/students`
  return axios.post(url, {sids}, {cancelToken: $_getStudentsCancel.token}).then(response => response.data)
}

export function toggleCampusRequirement(categoryId: number, isSatisfied: boolean) {
  const url: string = `${utils.apiBaseUrl()}/api/degree/category/${categoryId}/satisfy`
  return axios.post(url, {isSatisfied}).then(response => response.data)
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
  const url: string = `${utils.apiBaseUrl()}/api/degree/course/${courseId}/update`
  return axios.post(url, data).then(response => response.data)
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
  const url: string = `${utils.apiBaseUrl()}/api/degree/category/${categoryId}/recommend`
  return axios.post(url, data).then(response => response.data)
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
  const url: string = `${utils.apiBaseUrl()}/api/degree/category/${categoryId}/update`
  return axios.post(url, data).then(response => response.data)
}

export function updateDegreeNote(templateId: number, body: string) {
  const url: string = `${utils.apiBaseUrl()}/api/degree/${templateId}/note`
  return axios.post(url, {body}).then(response => response.data)
}

export function updateDegreeTemplate(templateId: number, name: string) {
  $_track('update', 'Degree Template')
  const url: string = `${utils.apiBaseUrl()}/api/degree/${templateId}/update`
  return axios.post(url, {name}).then(response => response.data)
}

export function updateUnitRequirement(unitRequirementId: number, name: string, minUnits: number) {
  const url: string = `${utils.apiBaseUrl()}/api/degree/unit_requirement/${unitRequirementId}/update`
  return axios.post(url, {name, minUnits}).then(response => response.data)
}
