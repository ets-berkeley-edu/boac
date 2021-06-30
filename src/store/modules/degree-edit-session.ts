import _ from 'lodash'
import Vue from 'vue'
import {
  addUnitRequirement,
  assignCourse,
  copyCourseAndAssign,
  createDegreeCategory,
  deleteDegreeCategory,
  deleteDegreeCourse,
  deleteUnitRequirement,
  getDegreeTemplate,
  updateCategory,
  updateCourse,
  updateDegreeNote,
  updateUnitRequirement
} from '@/api/degree'

const VALID_DRAG_DROP_CONTEXTS = ['assigned', 'ignored', 'requirement', 'unassigned']

const $_allowCourseDrop = (category, course, context) => {
  if (category) {
    const getCourseKey = c => c && `${c.termId}-${c.sectionId}`
    return (category.categoryType !== 'Course Requirement' || !category.courses.length)
      && (category.categoryType !== 'Category' || !category.subcategories.length)
      && !_.map(category.courses, getCourseKey).includes(getCourseKey(course))
  } else if (context) {
    return !course.isCopy && _.includes(['ignored', 'unassigned'], context)
  }
}

const $_debug = message => Vue.prototype.$config.isVueAppDebugMode && console.log(message)

const $_dropToAssign = (categoryId, commit, course, ignore, state) => {
  commit('setDisableButtons', true)
  return assignCourse(course.id, categoryId, ignore).then(() => {
    $_refresh(commit, state.templateId).then(() => {
      commit('draggingContextReset')
      commit('setDisableButtons', false)
    })
  })
}

const $_resetDraggingContext = state => state.draggingContext = {
  course: undefined,
  dragContext: undefined,
  target: undefined
}

const $_refresh = (commit, templateId) => {
  return new Promise<void>(resolve => {
    getDegreeTemplate(templateId).then((template: any) => {
      commit('resetSession', template)
      return resolve()
    })
  })
}

const state = {
  addCourseMenuOptions: undefined,
  batchSavedAlert: undefined,
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
  templateId: undefined,
  unitRequirements: undefined,
  updatedAt: undefined,
  updatedBy: undefined
}

const getters = {
  addCourseMenuOptions: (state: any): any[] => state.addCourseMenuOptions,
  batchSavedAlert: (state: any): string => state.batchSavedAlert,
  categories: (state: any): any[] => state.categories,
  courses: (state: any): any[] => state.courses,
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
  draggingContextReset: (state: any) => $_resetDraggingContext(state),
  dragStart: (state: any, {course, dragContext}) => state.draggingContext = {course, dragContext, target: undefined},
  dismissAlert: (state: any, templateId: number) => state.dismissedAlerts.push(templateId),
  resetSession: (state: any, template: any) => {
    state.disableButtons = false
    $_resetDraggingContext(state)
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
  setBatchSavedAlert: (state: any, message: any) => state.batchSavedAlert = message,
  setDisableButtons: (state: any, disableAll: any) => state.disableButtons = disableAll,
  setDraggingTarget: (state: any, target: any) => state.draggingContext.target = target,
  setIncludeNotesWhenPrint: (state: any, include: any) => state.includeNotesWhenPrint = include
}

const actions = {
  assignCourseToCategory: ({commit, state}, {course, category, ignore}) => {
    return new Promise<void>(resolve => {
      const categoryId = category && category.id
      assignCourse(course.id, categoryId, ignore).then(() => $_refresh(commit, state.templateId)).then(resolve)
    })
  },
  copyCourseAndAssign: ({commit, state}, {categoryId, sectionId, sid, termId}) => {
    return new Promise(resolve => {
      copyCourseAndAssign(categoryId, sectionId, sid, termId).then(course => {
        $_refresh(commit, state.templateId)
        resolve(course)
      })
    })
  },
  createCategory: ({commit, state}, {
    categoryType,
    description,
    name,
    parentCategoryId,
    position,
    unitRequirementIds,
    unitsLower,
    unitsUpper
  }) => {
    return new Promise(resolve => {
      createDegreeCategory(
        categoryType,
        description,
        name,
        parentCategoryId,
        position,
        state.templateId,
        unitRequirementIds,
        unitsLower,
        unitsUpper
      ).then(category => {
        $_refresh(commit, state.templateId).then(() => resolve(category))
      })
    })
  },
  createUnitRequirement: ({commit, state}, {name, minUnits}) => {
    return new Promise<void>(resolve => {
      addUnitRequirement(state.templateId, name, minUnits).then(() => $_refresh(commit, state.templateId)).then(resolve)
    })
  },
  deleteCategory: ({commit, state}, categoryId: number) => {
    return new Promise(resolve => {
      deleteDegreeCategory(categoryId).then(() => $_refresh(commit, state.templateId)).then(resolve)
    })
  },
  deleteCourse: ({commit, state}, courseId: number) => {
    return new Promise(resolve => {
      deleteDegreeCourse(courseId).then(() => $_refresh(commit, state.templateId)).then(resolve)
    })
  },
  deleteUnitRequirement: ({commit, state}, unitRequirementId: number) => {
    return new Promise<void>(resolve => {
      deleteUnitRequirement(unitRequirementId).then(() => $_refresh(commit, state.templateId)).then(resolve)
    })
  },
  dismissAlert: ({commit}, templateId: number) => commit('dismissAlert', templateId),
  setBatchSavedAlert: ({commit}, message: any) => commit('setBatchSavedAlert', message),
  setDraggingTarget: ({commit}, target: any) => commit('setDraggingTarget', target),
  init: ({commit}, templateId: number) => new Promise<void>(resolve => $_refresh(commit, templateId).then(resolve)),
  onDragEnd: ({commit}) => commit('draggingContextReset'),
  onDragStart: ({commit}, {course, dragContext}) => commit('dragStart', {course, dragContext}),
  onDrop: ({commit}, {category, context}) => {
    return new Promise<void>(resolve => {
      const course = state.draggingContext.course
      const dragContext = state.draggingContext.dragContext
      const actionByUser = `${dragContext} to ${context}`

      const done = (srAlert: string, noActionTaken?: boolean) => {
        Vue.prototype.$announcer.polite(srAlert)
        if (noActionTaken) {
          $_debug(srAlert)
        } else {
          if (_.includes(['ignored', 'unassigned'], context)) {
            $_debug(`Course ${_.get(course, 'id')} (${dragContext}) dragged to ${context} section.`)
          } else {
            $_debug(`From ${actionByUser}: course ${_.get(course, 'id')} (${dragContext}) dragged to category ${_.get(category, 'id')} (${context})`)
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
  updateCourse: ({commit, state}, {courseId, note, unitRequirementIds, units}) => {
    return new Promise(resolve => {
      updateCourse(courseId, note, unitRequirementIds, units).then(data => {
        $_refresh(commit, state.templateId).then(() => resolve(data))
      })
    })
  },
  updateNote: ({commit, state}, noteBody: string) => {
    return new Promise<void>(resolve => {
      updateDegreeNote(state.templateId, noteBody).then((note: any) => {
        $_refresh(commit, state.templateId).then(() => resolve(note))
      })
    })
  },
  updateUnitRequirement: ({commit, state}, {name, minUnits, unitRequirementId}) => {
    return new Promise<void>(resolve => {
      updateUnitRequirement(unitRequirementId, name, minUnits).then(() => $_refresh(commit, state.templateId)).then(resolve)
    })
  },
  updateCategory: ({commit, state}, {
    categoryId,
    description,
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
        name,
        parentCategoryId,
        unitRequirementIds,
        unitsLower,
        unitsUpper
      ).then(() => $_refresh(commit, state.templateId)).then(resolve)
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
