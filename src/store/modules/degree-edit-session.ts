import _ from 'lodash'
import {
  addUnitRequirement,
  assignCourse,
  copyCourseAndAssign,
  createDegreeCategory,
  deleteDegreeCategory,
  deleteUnitRequirement,
  getDegreeTemplate,
  updateCourse,
  updateDegreeCategory,
  updateDegreeNote,
  updateUnitRequirement
} from '@/api/degree'

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
  updateUnitRequirement: (state: any, {index, unitRequirement}) => state.unitRequirements[index] = unitRequirement
}

const actions = {
  assignCourseToCategory: ({commit, state}, {course, category}) => {
    return new Promise<void>(resolve => {
      const categoryId = category && category.id
      assignCourse(categoryId, course.id).then(() => $_refresh(commit, state.templateId)).then(resolve)
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
    units
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
        units
      ).then(category => {
        $_refresh(commit, state.templateId).then(() => resolve(category))
      }
      )
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
  setDisableButtons: ({commit}, disable: boolean) => commit('setDisableButtons', disable),
  updateCourse: ({commit, state}, {courseId, note, units}) => {
    return new Promise(resolve => {
      updateCourse(courseId, note, units).then(data => {
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
    units
  }) => {
    return new Promise(resolve => {
      updateDegreeCategory(
        categoryId,
        description,
        name,
        parentCategoryId,
        unitRequirementIds,
        units
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
