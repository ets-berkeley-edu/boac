import _ from 'lodash'
import {
  addUnitRequirement,
  assignCourse,
  copyCourseAndAssign,
  createDegreeCategory,
  deleteDegreeCategory,
  deleteUnitRequirement,
  getDegreeTemplate,
  updateCategory,
  updateCourse,
  updateDegreeNote,
  updateUnitRequirement
} from '@/api/degree'

const VALID_DRAG_DROP_CONTEXTS = ['assigned', 'unassigned']

const $_debugDragAndDrop = (action, state, {category, course, dropContext, student}) => {
  console.log(`
    ---
    ACTION: ${action}
    FROM: {
      category: ${state.draggingContext.category && state.draggingContext.category.id},
      dragContext: ${state.draggingContext.dragContext},
      course: ${state.draggingContext.course && state.draggingContext.course.id},
      student: ${state.draggingContext.student && state.draggingContext.student.sid}
    }
    TO: {
      category: ${category && category.id},
      dropContext: ${dropContext},
      course: ${course && course.id},
      student: ${student && student.sid}
    }
    ---
  `)
}

const $_dropToAssign = (categoryId, commit, courseId, state) => {
  commit('setDisableButtons', true)
  return assignCourse(courseId, categoryId).then(() => {
    $_refresh(commit, state.templateId).then(() => {
      commit('draggingContextReset')
      commit('setDisableButtons', false)
    })
  })
}

const $_resetDraggingContext = state => state.draggingContext = {
  category: undefined,
  dragContext: undefined,
  course: undefined,
  student: undefined
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
  categories: undefined,
  courses: undefined,
  createdAt: undefined,
  createdBy: undefined,
  degreeName: undefined,
  degreeNote: undefined,
  disableButtons: false,
  draggingContext: {
    category: undefined,
    dragContext: undefined,
    course: undefined,
    student: undefined
  },
  includeNotesWhenPrint: true,
  sid: undefined,
  templateId: undefined,
  unitRequirements: undefined,
  updatedAt: undefined,
  updatedBy: undefined
}

const getters = {
  addCourseMenuOptions: (state: any): any[] => state.addCourseMenuOptions,
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
  includeNotesWhenPrint: (state: any): boolean => state.includeNotesWhenPrint,
  sid: (state: any): string => state.sid,
  templateId: (state: any): number => state.templateId,
  unitRequirements: (state: any): any[] => state.unitRequirements,
  updatedAt: (state: any): any[] => state.updatedAt,
  updatedBy: (state: any): any[] => state.updatedBy
}

const mutations = {
  addUnitRequirement: (state: any, unitRequirement: any) => state.unitRequirements.push(unitRequirement),
  removeUnitRequirement: (state: any, index: number) => state.unitRequirements.splice(index, 1),
  resetSession: (state: any, template: any) => {
    state.disableButtons = false
    if (template) {
      state.categories = template.categories
      state.courses = template.courses
      state.createdAt = template.createdAt
      state.createdBy = template.createdBy
      state.degreeName = template.name
      state.degreeNote = template.note
      state.templateId = template.id
      state.sid = template.sid
      state.unitRequirements = template.unitRequirements
      state.updatedAt = template.updatedAt
      state.updatedBy = template.updatedBy
    } else {
      state.categories = state.createdAt = state.createdBy = state.degreeName = state.degreeNote = undefined
      state.templateId = state.sid = state.unitRequirements = state.updatedAt = state.updatedBy = undefined
    }
  },
  setDisableButtons: (state: any, disableAll: any) => state.disableButtons = disableAll,
  draggingContextReset: (state: any) => $_resetDraggingContext(state),
  dragStart: (state: any, {category, course, dragContext, student}) => state.draggingContext = {category, course, dragContext, student},
  setIncludeNotesWhenPrint: (state: any, include: any) => state.includeNotesWhenPrint = include,
  updateUnitRequirement: (state: any, {index, unitRequirement}) => state.unitRequirements[index] = unitRequirement
}

const actions = {
  assignCourseToCategory: ({commit, state}, {course, category}) => {
    return new Promise<void>(resolve => {
      const categoryId = category && category.id
      assignCourse(course.id, categoryId).then(() => $_refresh(commit, state.templateId)).then(resolve)
    })
  },
  copyCourseAndAssign: ({commit, state}, {categoryId, sectionId, sid, termId}) => {
    return new Promise<void>(resolve => {
      copyCourseAndAssign(categoryId, sectionId, sid, termId).then(() => $_refresh(commit, state.templateId)).then(resolve)
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
      addUnitRequirement(state.templateId, name, minUnits).then(unitRequirement => {
        commit('addUnitRequirement', unitRequirement)
        resolve()
      })
    })
  },
  deleteCategory: ({commit, state}, categoryId: number) => {
    return new Promise(resolve => {
      deleteDegreeCategory(categoryId).then(() => $_refresh(commit, state.templateId)).then(resolve)
    })
  },
  deleteUnitRequirement: ({commit, state}, index: number) => {
    return new Promise<void>(resolve => {
      const id = _.get(state.unitRequirements[index], 'id')
      deleteUnitRequirement(id).then(() => {
        commit('removeUnitRequirement', index)
        resolve()
      })
    })
  },
  init: ({commit}, templateId: number) => new Promise<void>(resolve => $_refresh(commit, templateId).then(resolve)),
  onDragStart: ({commit}, {category, course, dragContext, student}) => commit('dragStart', {category, course, dragContext, student}),
  onDrop: ({commit}, {category, course, dropContext, student}) => {
    $_debugDragAndDrop('onDrop', state, {category, course, dropContext, student})
    return new Promise(resolve => {
      const dragContext = state.draggingContext.dragContext
      const valid = _.includes(VALID_DRAG_DROP_CONTEXTS, dragContext) && _.includes(VALID_DRAG_DROP_CONTEXTS, dropContext)
      if (valid) {
        const courseId = _.get(state.draggingContext.course, 'id')
        if (dragContext === 'assigned' && dropContext === 'unassigned') {
          $_dropToAssign(null, commit, courseId, state).then(resolve)
        } else if (dragContext === 'unassigned' && dropContext === 'assigned') {
          $_dropToAssign(_.get(category, 'id'), commit, courseId, state).then(resolve)
        } else {
          commit('draggingContextReset').then(() => {
            throw new ReferenceError(`Unrecognized transaction type where dragContext = '${dragContext}' and dropContext = '${dropContext}'`)
          })
        }
      } else {
        commit('draggingContextReset').then(() => {
          throw new TypeError(`Invalid context(s): dragContext = '${dragContext}' and dropContext = '${dropContext}'`)
        })
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
  updateUnitRequirement: ({commit, state}, {index, name, minUnits}) => {
    return new Promise<void>(resolve => {
      const id = _.get(state.unitRequirements[index], 'id')
      updateUnitRequirement(id, name, minUnits).then(
        unitRequirement => {
          commit('updateUnitRequirement', {index, unitRequirement})
          resolve()
        }
      )
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
