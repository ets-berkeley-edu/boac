import {concat, each, filter, find, get, includes, isEmpty, isNaN, isNil, map, startsWith} from 'lodash'
import {useDegreeStore} from '@/stores/degree-edit-session'

export type CourseRequirement = {
  categoryType: ('Course Requirement' | 'Campus Requirement'),
  courses: DegreeProgressCourse[],
  id: number
}

export type Category = {
  categoryType: 'Category',
  courseRequirements: CourseRequirement[],
  courses: DegreeProgressCourse[],
  id: number,
  name: string,
  subcategories: Category[]
}

export type DegreeProgressCourse = {
  id: number,
  manuallyCreatedAt: string,
  manuallyCreatedBy: number,
  sectionId: number,
  sis: {
    units: number
  },
  termId: number,
  units: number
}

export type DegreeProgressCourses = {
  assigned: DegreeProgressCourse[],
  unassigned: DegreeProgressCourse[]
}

export type DraggingContext = {
  course: DegreeProgressCourse | undefined,
  dragContext: unknown | undefined,
  target: unknown | undefined
}

export type DegreeTemplate = {
  categories: object[] | undefined,
  courses: DegreeProgressCourse[] | undefined,
  createdAt: string | undefined,
  createdBy: string | undefined,
  id: number,
  name: string | undefined,
  note: string | undefined,
  parentTemplateId: string | undefined,
  parentTemplateUpdatedAt: string | undefined,
  sid: string | undefined,
  unitRequirements: object[] | undefined,
  updatedAt: string | undefined,
  updatedBy: string | undefined
}

export const MAX_UNITS_ALLOWED = 10

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
  if (courses) {
    const categoryCourseIds: number[] = map(category.courses, 'id')
    const predicate = (c: DegreeProgressCourse) => includes(categoryCourseIds, c.id)
    const items: Array<DegreeProgressCourse|CourseRequirement> = (filter(courses.assigned.concat(courses.unassigned), predicate))
    items.concat(category.courseRequirements)
    return items
  } else {
    return category.courseRequirements
  }
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
export function validateUnitRange(unitsLower: number, unitsUpper: number, maxAllowed: number, showUnitsUpperInput?: boolean): object {
  const invalid = message => ({valid: false, message})
  const message = `must be a number between 0 and ${maxAllowed}`
  if (isValidUnits(unitsLower, maxAllowed)) {
    if (isNil(unitsUpper)) {
      return {valid: true}
    } else {
      if (isValidUnits(unitsUpper, maxAllowed)) {
        const empty = isEmpty(unitsLower) && isEmpty(unitsUpper)
        return empty || parseFloat(String(unitsLower)) <= parseFloat(String(unitsUpper)) ? {valid: true} : invalid('Units upper range value must be greater than lower range value.')
      } else {
        return invalid(`Units upper range value ${message}.`)
      }
    }
  } else {
    return invalid(showUnitsUpperInput ? `Units lower range value ${message}.` : `Units ${message}`)
  }
}
