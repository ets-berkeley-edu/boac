import store from '@/store'
import {alertScreenReader} from '@/store/modules/context'
import {assignCourse, deleteDegreeCategory, deleteDegreeCourse, getDegreeTemplate} from '@/api/degree'
import {get, includes, map} from 'lodash'

const VALID_DRAG_DROP_CONTEXTS: string[] = ['assigned', 'ignored', 'requirement', 'unassigned']

const $_allowCourseDrop = (category, course, context): boolean => {
  if (category) {
    const getCourseKey = (c: any): string | null => {
      return c ? `${c.termId}-${c.sectionId}-${c.manuallyCreatedAt}-${c.manuallyCreatedBy}` : null
    }
    return (category.categoryType !== 'Course Requirement' || !category.courses.length)
      && (category.categoryType !== 'Category' || !category.subcategories.length)
      && !map(category.courses, getCourseKey).includes(getCourseKey(course))
  } else if (context) {
    return includes(['ignored', 'unassigned'], context)
  }
  return false
}

const $_dropToAssign = (categoryId: number | null, course: any, ignore: boolean) => {
  store.commit('degree/setDisableButtons', true)
  return assignCourse(course.id, categoryId, ignore).then(() => {
    const templateId = store.getters['degree/templateId']
    refreshDegreeTemplate(templateId).then(() => {
      store.commit('degree/draggingContextReset')
      store.commit('degree/setDisableButtons', false)
    })
  })
}

export function deleteCategory(categoryId: number) {
  return new Promise(resolve => {
    const templateId: number = store.getters['degree/templateId']
    deleteDegreeCategory(categoryId).then(() => refreshDegreeTemplate(templateId)).then(resolve)
  })
}

export function deleteCourse(courseId: number): Promise<any> {
  return new Promise(resolve => {
    const templateId: number = store.getters['degree/templateId']
    deleteDegreeCourse(courseId).then(() => refreshDegreeTemplate(templateId)).then(resolve)
  })
}

export function log(message: string) {
  store.getters['context/config'].isVueAppDebugMode && console.log(message)
}

export function onDrop(category: any, context: any) {
  return new Promise<void>(resolve => {
    const draggingContext = store.getters['degree/draggingContext']
    const course = draggingContext.course
    const dragContext = draggingContext.dragContext
    const actionByUser = `${dragContext} to ${context}`

    const done = (srAlert: string, noActionTaken?: boolean) => {
      alertScreenReader(srAlert)
      if (noActionTaken) {
        log(srAlert)
      } else {
        if (includes(['ignored', 'unassigned'], context)) {
          log(`Course ${get(course, 'id')} (${dragContext}) dragged to ${context} section.`)
        } else {
          log(`From ${actionByUser}: course ${get(course, 'id')} (${dragContext}) dragged to category ${get(category, 'id')} (${context})`)
        }
      }
      resolve()
    }
    const valid = includes(VALID_DRAG_DROP_CONTEXTS, dragContext) && includes(VALID_DRAG_DROP_CONTEXTS, context)
    if (valid) {
      switch (actionByUser) {
        case 'assigned to ignored':
        case 'assigned to unassigned':
        case 'ignored to unassigned':
        case 'unassigned to ignored':
          if ($_allowCourseDrop(null, course, context)) {
            $_dropToAssign(null, course, context === 'ignored').then(() => done(`Course ${context}`))
          } else {
            done('Drop canceled. No assignment made.', true)
          }
          break
        case 'assigned to assigned':
        case 'ignored to assigned':
        case 'unassigned to assigned':
          $_dropToAssign(category.id, course, false).then(() => done(`Course assigned to ${category.name}`))
          break
        case 'assigned to requirement':
        case 'ignored to requirement':
        case 'unassigned to requirement':
          if ($_allowCourseDrop(category, course, null)) {
            $_dropToAssign(category.id, course, false).then(() => done(`Course assigned to ${category.name}`))
          } else {
            done('Drop canceled. No assignment made.', true)
          }
          break
        case 'ignored to ignored':
        case 'unassigned to unassigned':
          done('Course not assigned.', true)
          break
        default:
          done(`Unrecognized operation: ${actionByUser}`, true)
          store.commit('degree/draggingContextReset')
          throw new TypeError(`Unrecognized transaction type where dragContext = '${dragContext}' and dropContext = '${context}'`)
      }

    } else {
      const message = `Invalid context(s): dragContext = '${dragContext}' and dropContext = '${context}'`
      done(message, true)
      store.commit('degree/draggingContextReset')
      throw new TypeError(message)
    }
  })
}

export function refreshDegreeTemplate(templateId: number): Promise<void> {
  return new Promise<void>(resolve => {
    getDegreeTemplate(templateId).then((template: any) => {
      store.commit('degree/resetSession', template)
      return resolve()
    })
  })
}
