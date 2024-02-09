import _ from 'lodash'
import {alertScreenReader} from '@/store/modules/context'
import {log, refreshDegreeTemplate} from '@/store/modules/degree-edit-session/utils'
import {
  assignCourse,
  deleteUnitRequirement,
  updateCategory,
  updateCourse,
  updateCourseRequirement,
  updateDegreeNote,
  updateUnitRequirement
} from '@/api/degree'

export type DegreeProgressCourses = {
  assigned: any[],
  unassigned: any[]
}

const VALID_DRAG_DROP_CONTEXTS: string[] = ['assigned', 'ignored', 'requirement', 'unassigned']

const $_allowCourseDrop = (category, course, context) => {
  if (category) {
    const getCourseKey = c => c && `${c.termId}-${c.sectionId}-${c.manuallyCreatedAt}-${c.manuallyCreatedBy}`
    return (category.categoryType !== 'Course Requirement' || !category.courses.length)
      && (category.categoryType !== 'Category' || !category.subcategories.length)
      && !_.map(category.courses, getCourseKey).includes(getCourseKey(course))
  } else if (context) {
    return _.includes(['ignored', 'unassigned'], context)
  }
}

const $_dropToAssign = (categoryId, commit, course, ignore, state) => {
  commit('setDisableButtons', true)
  return assignCourse(course.id, categoryId, ignore).then(() => {
    refreshDegreeTemplate(state.templateId).then(() => {
      commit('draggingContextReset')
      commit('setDisableButtons', false)
    })
  })
}

type DraggingContext = {
  course: any,
  dragContext: any,
  target: any
}

function $_getDefaultDraggingContext(): DraggingContext {
  return {
    course: undefined,
    dragContext: undefined,
    target: undefined
  }
}

const state = {
  addCourseMenuOptions: undefined,
  categories: undefined,
  courses: undefined,
  createdAt: undefined,
  createdBy: undefined,
  degreeName: undefined,
  degreeNote: undefined,
  disableButtons: false,
  dismissedAlerts: [],
  draggingContext: {
    course: undefined,
    dragContext: undefined,
    target: undefined
  },
  includeNotesWhenPrint: true,
  lastPageRefreshAt: undefined,
  parentTemplateId: undefined,
  parentTemplateUpdatedAt: undefined,
  sid: undefined,
  templateId: NaN,
  unitRequirements: undefined,
  updatedAt: undefined,
  updatedBy: undefined
}

const getters = {
  addCourseMenuOptions: (state: any): any[] => state.addCourseMenuOptions,
  categories: (state: any): any[] => state.categories,
  courses: (state: any): DegreeProgressCourses => state.courses,
  createdAt: (state: any): any[] => state.createdAt,
  createdBy: (state: any): any[] => state.createdBy,
  degreeEditSessionToString: (state: any): any => ({
    categories: state.categories,
    courses: state.courses,
    degreeName: state.degreeName,
    degreeNote: state.degreeNote,
    disableButtons: state.disableButtons,
    templateId: state.templateId,
    unitRequirements: state.unitRequirements
  }),
  degreeName: (state: any): string => state.degreeName,
  degreeNote: (state: any): string => state.degreeNote,
  disableButtons: (state: any): boolean => state.disableButtons,
  dismissedAlerts: (state: any): number[] => state.dismissedAlerts,
  draggingContext: (state: any): any => state.draggingContext,
  includeNotesWhenPrint: (state: any): boolean => state.includeNotesWhenPrint,
  isUserDragging: (state: any) => (courseId: number) => !!courseId && _.get(state.draggingContext.course, 'id') === courseId,
  lastPageRefreshAt: (state: any): any[] => state.lastPageRefreshAt,
  parentTemplateId: (state: any): string => state.parentTemplateId,
  parentTemplateUpdatedAt: (state: any): string => state.parentTemplateUpdatedAt,
  sid: (state: any): string => state.sid,
  templateId: (state: any): number => state.templateId,
  unitRequirements: (state: any): any[] => state.unitRequirements,
  updatedAt: (state: any): any[] => state.updatedAt,
  updatedBy: (state: any): any[] => state.updatedBy
}

const mutations = {
  draggingContextReset: (state: any) => state.draggingContext = $_getDefaultDraggingContext(),
  dragStart: (state: any, {course, dragContext}) => state.draggingContext = {course, dragContext, target: undefined},
  dismissAlert: (state: any, templateId: number) => state.dismissedAlerts.push(templateId),
  resetSession: (state: any, template: any) => {
    state.disableButtons = false
    state.draggingContext = $_getDefaultDraggingContext()
    if (template) {
      state.categories = template.categories
      state.courses = template.courses
      state.createdAt = template.createdAt
      state.createdBy = template.createdBy
      state.degreeName = template.name
      state.degreeNote = template.note
      state.parentTemplateId = template.parentTemplateId
      state.parentTemplateUpdatedAt = template.parentTemplateUpdatedAt
      state.sid = template.sid
      state.templateId = template.id
      state.unitRequirements = template.unitRequirements
      state.updatedAt = template.updatedAt
      state.updatedBy = template.updatedBy
    } else {
      state.categories = state.createdAt = state.createdBy = state.degreeName = state.degreeNote = undefined
      state.parentTemplateId = state.parentTemplateUpdatedAt = undefined
      state.templateId = state.sid = state.unitRequirements = state.updatedAt = state.updatedBy = undefined
    }
    state.lastPageRefreshAt = new Date()
  },
  setDisableButtons: (state: any, disableAll: any) => state.disableButtons = disableAll,
  setDraggingTarget: (state: any, target: any) => state.draggingContext.target = target,
  setIncludeNotesWhenPrint: (state: any, include: any) => state.includeNotesWhenPrint = include
}

const actions = {
  deleteUnitRequirement: ({state}, unitRequirementId: number) => {
    return new Promise<void>(resolve => {
      deleteUnitRequirement(unitRequirementId).then(() => refreshDegreeTemplate(state.templateId)).then(resolve)
    })
  },
  dismissAlert: ({commit}, templateId: number) => commit('dismissAlert', templateId),
  setDraggingTarget: ({commit}, target: any) => commit('setDraggingTarget', target),
  onDragEnd: ({commit}) => commit('draggingContextReset'),
  onDragStart: ({commit}, {course, dragContext}) => commit('dragStart', {course, dragContext}),
  onDrop: ({commit}, {category, context}) => {
    return new Promise<void>(resolve => {
      const course = state.draggingContext.course
      const dragContext = state.draggingContext.dragContext
      const actionByUser = `${dragContext} to ${context}`

      const done = (srAlert: string, noActionTaken?: boolean) => {
        alertScreenReader(srAlert)
        if (noActionTaken) {
          log(srAlert)
        } else {
          if (_.includes(['ignored', 'unassigned'], context)) {
            log(`Course ${_.get(course, 'id')} (${dragContext}) dragged to ${context} section.`)
          } else {
            log(`From ${actionByUser}: course ${_.get(course, 'id')} (${dragContext}) dragged to category ${_.get(category, 'id')} (${context})`)
          }
        }
        resolve()
      }
      const valid = _.includes(VALID_DRAG_DROP_CONTEXTS, dragContext) && _.includes(VALID_DRAG_DROP_CONTEXTS, context)
      if (valid) {
        switch (actionByUser) {
          case 'assigned to ignored':
          case 'assigned to unassigned':
          case 'ignored to unassigned':
          case 'unassigned to ignored':
            if ($_allowCourseDrop(null, course, context)) {
              $_dropToAssign(null, commit, course, context === 'ignored', state).then(() => done(`Course ${context}`))
            } else {
              done('Drop canceled. No assignment made.', true)
            }
            break
          case 'assigned to assigned':
          case 'ignored to assigned':
          case 'unassigned to assigned':
            $_dropToAssign(category.id, commit, course, false, state).then(() => done(`Course assigned to ${category.name}`))
            break
          case 'assigned to requirement':
          case 'ignored to requirement':
          case 'unassigned to requirement':
            if ($_allowCourseDrop(category, course, null)) {
              $_dropToAssign(category.id, commit, course, false, state).then(() => done(`Course assigned to ${category.name}`))
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
            commit('draggingContextReset')
            throw new TypeError(`Unrecognized transaction type where dragContext = '${dragContext}' and dropContext = '${context}'`)
        }

      } else {
        const message = `Invalid context(s): dragContext = '${dragContext}' and dropContext = '${context}'`
        done(message, true)
        commit('draggingContextReset')
        throw new TypeError(message)
      }
    })
  },
  setDisableButtons: ({commit}, disable: boolean) => commit('setDisableButtons', disable),
  setIncludeNotesWhenPrint: ({commit}, include: boolean) => commit('setIncludeNotesWhenPrint', include),
  updateCategory: ({state}, {
    categoryId,
    description,
    isSatisfiedByTransferCourse,
    name,
    parentCategoryId,
    unitRequirementIds,
    unitsLower,
    unitsUpper
  }) => {
    return new Promise(resolve => {
      updateCategory(
        categoryId,
        description,
        isSatisfiedByTransferCourse,
        name,
        parentCategoryId,
        unitRequirementIds,
        unitsLower,
        unitsUpper
      ).then(() => refreshDegreeTemplate(state.templateId)).then(resolve)
    })
  },
  updateCourse: ({state}, {
    accentColor,
    grade,
    courseId,
    name,
    note,
    unitRequirementIds,
    units
  }) => {
    return new Promise(resolve => {
      updateCourse(
        accentColor,
        courseId,
        grade,
        name,
        note,
        unitRequirementIds,
        units
      ).then(data => {
        refreshDegreeTemplate(state.templateId).then(() => resolve(data))
      })
    })
  },
  updateCourseRequirement: ({state}, {
    accentColor,
    categoryId,
    grade,
    isIgnored,
    isRecommended,
    note,
    unitsLower,
    unitsUpper
  }) => {
    return new Promise(resolve => {
      updateCourseRequirement(
        accentColor,
        categoryId,
        grade,
        isIgnored,
        isRecommended,
        note,
        unitsLower,
        unitsUpper
      ).then(() => refreshDegreeTemplate(state.templateId)).then(resolve)
    })
  },
  updateNote: ({state}, noteBody: string) => {
    return new Promise<void>(resolve => {
      updateDegreeNote(state.templateId, noteBody).then((note: any) => {
        refreshDegreeTemplate(state.templateId).then(() => resolve(note))
      })
    })
  },
  updateUnitRequirement: ({state}, {name, minUnits, unitRequirementId}) => {
    return new Promise<void>(resolve => {
      updateUnitRequirement(unitRequirementId, name, minUnits).then(() => refreshDegreeTemplate(state.templateId)).then(resolve)
    })
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}
