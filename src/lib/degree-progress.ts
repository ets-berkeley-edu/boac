import {concat, each, filter, find, get, includes, isEmpty, isNaN, isNil, map, startsWith, trim} from 'lodash'
import type {Category, CourseRequirement, DegreeProgressCourse, DegreeProgressCourses, DegreeTemplate} from '@/lib/types'
import {useDegreeStore} from '@/stores/degree-edit-session'

export const MAX_UNITS_ALLOWED = 10

interface ValidationReport {valid: boolean, message: string}

export function categoryHasCourse(category: Category, course: DegreeProgressCourse): boolean {
  let courses: DegreeProgressCourse[] = []
  const extractCourses = (c: Category) => {
    courses = courses.concat(c.courses)
    each(c.courseRequirements, r => courses = courses.concat(r.courses))
  }
  extractCourses(category)
  each(category.subcategories, subcategory => extractCourses(subcategory))
  return map(courses, getCourseKey).includes(getCourseKey(course))
}

export function findCategoryById(categoryId: number) {
  const categories: Category[] = useDegreeStore().categories
  return categoryId ? find(flattenCategories(categories), ['id', categoryId]) : null
}

export function flattenCategories(categories: Category[]) {
  let flattened: (Category | CourseRequirement)[] = []
  each(categories, (category: Category) => {
    flattened.push(category)
    each(category.courseRequirements, (child: CourseRequirement) => {
      flattened.push(child)
    })
    each(category.subcategories || [], (child: Category) => {
      flattened.push(child)
      if (get (child, 'courseRequirements')) {
        flattened = concat(flattened, child.courseRequirements)
      }
    })
  })
  return flattened
}

export function getAssignedCourses(category: Category, ignoreCourseId: number): DegreeProgressCourse[] {
  const assigned: DegreeProgressCourse[] = []
  each(flattenCategories([category]), c => {
    each(c.courses, course => {
      if ((course.sectionId || course.manuallyCreatedBy) && (!ignoreCourseId || course.id !== ignoreCourseId)) {
        assigned.push(course)
      }
    })
  })
  return assigned
}

export function getCourseKey(course: DegreeProgressCourse) {
  return course && `${course.termId}-${course.sectionId}-${course.manuallyCreatedAt}-${course.manuallyCreatedBy}`
}

export function getItemsForCoursesTable(category: Category): Array<DegreeProgressCourse|CourseRequirement> {
  const courses: DegreeProgressCourses = useDegreeStore().courses
  let items: Array<DegreeProgressCourse|CourseRequirement>
  if (courses) {
    const categoryCourseIds: number[] = map(category.courses, 'id')
    const predicate = (c: DegreeProgressCourse) => includes(categoryCourseIds, c.id)
    items = filter(courses.assigned.concat(courses.unassigned), predicate)
    items.push(...category.courseRequirements)
  } else {
    items = category.courseRequirements
  }
  return items
}

export function isCampusRequirement(courseRequirement: CourseRequirement): boolean {
  return startsWith(courseRequirement.categoryType, 'Campus Requirement')
}

export function isValidUnits(value: number, maxAllowed: number): boolean {
  return !isNaN(value) && value > 0 && value <= maxAllowed
}

export function unitsWereEdited(course: DegreeProgressCourse): boolean {
  return !get(course, 'manuallyCreatedBy') && !isNil(get(course, 'units')) && !isNil(get(course, 'sis.units')) && (course.units !== course.sis.units)
}

export function validateDegreeTemplateName(templateName: string, existingTemplates: DegreeTemplate[]): ValidationReport {
  const registerAsInvalid = (message: string): ValidationReport => ({valid: false, message})
  let report: ValidationReport = {valid: true, message: ''}
  if (!trim(templateName)) {
    report = registerAsInvalid('Degree Name is required')
  } else {
    const lower = trim(templateName).toLowerCase()
    if (map(existingTemplates, 'name').findIndex((s: string|undefined) => (s || '').toLowerCase() === lower) >= 0) {
      report = registerAsInvalid(`A degree named <span class="font-weight-600">'${templateName}'</span> already exists. Please choose a different name.`)
    }
  }
  return report
}

export function validateUnitRange(unitsLower: number, unitsUpper: number, maxAllowed: number, showUnitsUpperInput?: boolean): ValidationReport {
  const registerAsInvalid = (message: string): ValidationReport => ({valid: false, message})
  let report: ValidationReport
  const suffix = `must be a number between 0 and ${maxAllowed}`
  if (isValidUnits(unitsLower, maxAllowed)) {
    if (isNil(unitsUpper)) {
      report = {valid: true, message: ''}
    } else {
      if (isValidUnits(unitsUpper, maxAllowed)) {
        const empty = isEmpty(unitsLower) && isEmpty(unitsUpper)
        report = empty || parseFloat(String(unitsLower)) <= parseFloat(String(unitsUpper)) ? {valid: true, message: ''} : registerAsInvalid('Units upper range value must be greater than lower range value.')
      } else {
        report = registerAsInvalid(`Units upper range value ${suffix}.`)
      }
    }
  } else {
    report = registerAsInvalid(showUnitsUpperInput ? `Units lower range value ${suffix}.` : `Units ${suffix}`)
  }
  return report
}
