import _ from 'lodash'
import {
  addUnitRequirement,
  assignCourse,
  createDegreeCategory,
  deleteDegreeCategory,
  deleteUnitRequirement,
  getDegreeTemplate, getUnassignedCourses,
  updateDegreeCategory,
  updateDegreeNote,
  updateUnitRequirement
} from '@/api/degree'
import store from '@/store'

const EDIT_MODE_TYPES = ['createUnitRequirement', 'updateUnitRequirement']

const state = {
  categories: undefined,
  createdAt: undefined,
  createdBy: undefined,
  degreeName: undefined,
  degreeNote: undefined,
  disableButtons: false,
  editMode: undefined,
  sid: undefined,
  templateId: undefined,
  unassignedCourses: undefined,
  unitRequirements: undefined,
  updatedAt: undefined,
  updatedBy: undefined
}

const getters = {
  categories: (state: any): any[] => state.categories,
  createdAt: (state: any): any[] => state.createdAt,
  createdBy: (state: any): any[] => state.createdBy,
  degreeEditSessionToString: (state: any): any => ({
    categories: state.categories,
    degreeName: state.degreeName,
    degreeNote: state.degreeNote,
    disableButtons: state.disableButtons,
    editMode: state.editMode,
    templateId: state.templateId,
    unitRequirements: state.unitRequirements
  }),
  degreeName: (state: any): string => state.degreeName,
  degreeNote: (state: any): string => state.degreeNote,
  disableButtons: (state: any): boolean => state.disableButtons,
  editMode: (state: any): string => state.editMode,
  sid: (state: any): number => state.sid,
  templateId: (state: any): number => state.templateId,
  unassignedCourses: (state: any): any[] => state.unassignedCourses,
  unitRequirements: (state: any): any[] => state.unitRequirements,
  updatedAt: (state: any): any[] => state.updatedAt,
  updatedBy: (state: any): any[] => state.updatedBy
}

const mutations = {
  addUnitRequirement: (state: any, unitRequirement: any) => state.unitRequirements.push(unitRequirement),
  removeUnitRequirement: (state: any, index: number) => state.unitRequirements.splice(index, 1),
  resetSession: (state: any, template: any) => {
    state.editMode = null
    state.categories = template && template.categories
    state.createdAt = template && template.createdAt
    state.createdBy = template && template.createdBy
    state.degreeName = template && template.name
    state.degreeNote = template && template.note
    state.templateId = template && template.id
    state.sid = template && template.sid
    state.unitRequirements = template && template.unitRequirements
    state.updatedAt = template && template.updatedAt
    state.updatedBy = template && template.updatedBy
  },
  setDisableButtons: (state: any, disableAll: any) => state.disableButtons = disableAll,
  setEditMode(state: any, editMode: string) {
    if (_.isNil(editMode)) {
      state.editMode = null
    } else if (_.find(EDIT_MODE_TYPES, type => editMode.match(type))) {
      // Valid mode
      state.editMode = editMode
    } else {
      throw new TypeError(`Invalid page mode: ${editMode}`)
    }
  },
  setUnassignedCourses: (state: any, unassignedCourses: any[]) => state.unassignedCourses = unassignedCourses,
  updateNote: (state: any, note: any) => state.degreeNote = note,
  updateUnitRequirement: (state: any, {index, unitRequirement}) => state.unitRequirements[index] = unitRequirement
}

const actions = {
  assignCourseToCategory: ({commit, state}, {course, category}) => {
    return new Promise<void>(resolve => {
      const categoryId = category && category.id
      assignCourse(categoryId, course.sectionId, course.sid, course.termId).then(() => {
          store.dispatch('degreeEditSession/loadTemplate', state.templateId).then(resolve)
          getUnassignedCourses(state.templateId).then(data => {
            commit('setUnassignedCourses', data)
            resolve()
          })
        }
      )
    })
  },
  createCategory: ({commit, state}, {
    categoryType,
    courseUnits,
    description,
    name,
    parentCategoryId,
    position,
    unitRequirementIds
  }) => {
    return new Promise<void>(resolve => {
      createDegreeCategory(
        categoryType,
        courseUnits,
        description,
        name,
        parentCategoryId,
        position,
        state.templateId,
        unitRequirementIds
      ).then(() => {
        store.dispatch('degreeEditSession/loadTemplate', state.templateId).then(() => {
          commit('setEditMode', null)
          resolve()
        })
      }
      )
    })
  },
  createUnitRequirement: ({commit, state}, {name, minUnits}) => {
    return new Promise<void>(resolve => {
      addUnitRequirement(state.templateId, name, minUnits).then(
        unitRequirement => {
          commit('addUnitRequirement', unitRequirement)
          commit('setEditMode', null)
          resolve()
        }
      )
    })
  },
  deleteCategory: ({state}, categoryId) => {
    return new Promise<void>(resolve => {
      deleteDegreeCategory(categoryId).then(() => {
        store.dispatch('degreeEditSession/loadTemplate', state.templateId).then(() => {
          resolve()
        })
      })
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
  init: ({commit}, templateId: number) => {
    return new Promise<void>(resolve => {
      if (templateId) {
        store.dispatch('degreeEditSession/loadTemplate', templateId).then(resolve)
      } else {
        commit('resetSession')
        resolve()
      }
    })
  },
  loadTemplate: ({commit}, templateId: number) => {
    return new Promise(resolve => {
      getUnassignedCourses(templateId).then(data => {
        commit('setUnassignedCourses', data)
        getDegreeTemplate(templateId).then((template: any) => {
          commit('resetSession', template)
          resolve(template)
        })
      })
    })
  },
  refreshUnassignedCourses: ({commit, state}) => {
    return new Promise<void>(resolve => {
      getUnassignedCourses(state.templateId).then(data => {
        commit('setUnassignedCourses', data)
        resolve()
      })
    })
  },
  setDisableButtons: ({commit}, disable: boolean) => commit('setDisableButtons', disable),
  setEditMode: ({commit}, editMode: string) => commit('setEditMode', editMode),
  updateNote: ({commit, state}, noteBody: string) => {
    return new Promise<void>(resolve => {
      updateDegreeNote(state.templateId, noteBody).then((note: any) => {
        commit('updateNote', note)
        resolve()
      })
    })
  },
  updateUnitRequirement: ({commit, state}, {index, name, minUnits}) => {
    return new Promise<void>(resolve => {
      const id = _.get(state.unitRequirements[index], 'id')
      updateUnitRequirement(id, name, minUnits).then(
        unitRequirement => {
          commit('updateUnitRequirement', {index, unitRequirement})
          commit('setEditMode', null)
          resolve()
        }
      )
    })
  },
  updateCategory: ({commit, state}, {
    categoryId,
    courseUnits,
    description,
    name,
    parentCategoryId,
    unitRequirementIds
  }) => {
    return new Promise<void>(resolve => {
      updateDegreeCategory(
        categoryId,
        courseUnits,
        description,
        name,
        parentCategoryId,
        unitRequirementIds
      ).then(() => {
        store.dispatch('degreeEditSession/loadTemplate', state.templateId).then(() => {
          commit('setEditMode', null)
          resolve()
        })
      }
      )
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
