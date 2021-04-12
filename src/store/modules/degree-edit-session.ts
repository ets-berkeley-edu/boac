import _ from 'lodash'
import {
  addUnitRequirement,
  createDegreeCategory,
  deleteDegreeCategory,
  getDegreeTemplate,
  updateUnitRequirement
} from '@/api/degree'
import store from '@/store'

const EDIT_MODE_TYPES = ['createUnitRequirement', 'updateUnitRequirement']

const state = {
  categories: undefined,
  degreeName: undefined,
  disableButtons: false,
  editMode: undefined,
  templateId: undefined,
  unitRequirements: undefined
}

const getters = {
  categories: (state: any): any[] => state.categories,
  degreeEditSessionToString: (state: any): any => ({
    categories: state.categories,
    degreeName: state.degreeName,
    disableButtons: state.disableButtons,
    editMode: state.editMode,
    templateId: state.templateId,
    unitRequirements: state.unitRequirements
  }),
  degreeName: (state: any): string => state.degreeName,
  disableButtons: (state: any): boolean => state.disableButtons,
  editMode: (state: any): string => state.editMode,
  templateId: (state: any): number => state.templateId,
  unitRequirements: (state: any): any[] => state.unitRequirements,
}

const mutations = {
  addDegreeCategory: (state: any, category: any) => state.categories.push(category),
  addUnitRequirement: (state: any, unitRequirement: any) => state.unitRequirements.push(unitRequirement),
  removeCategory: (state: any, categoryId: number) => state.categories = _.filter(state.categories, c => c.id !== categoryId),
  resetSession: (state: any, template: any) => {
    state.editMode = null
    state.categories = template && template.categories
    state.degreeName = template && template.name
    state.templateId = template && template.id
    state.unitRequirements = template && template.unitRequirements
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
  updateUnitRequirement: (state: any, {index, unitRequirement}) => {
    state.unitRequirements[index] = unitRequirement
  }
}

const actions = {
  createCategory: ({commit, state}, {
    categoryType,
    courseUnits,
    description,
    name,
    parentCategoryId,
    position,
    unitRequirementIds
  }) => {
    return new Promise(resolve => {
      createDegreeCategory(
        categoryType,
        courseUnits,
        description,
        name,
        parentCategoryId,
        position,
        state.templateId,
        unitRequirementIds
      ).then(category => {
        commit('addDegreeCategory', category)
        commit('setEditMode', null)
        resolve(category)
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
  deleteCategory: ({commit}, categoryId) => {
    return new Promise<void>(resolve => {
      deleteDegreeCategory(categoryId).then(() => {
        commit('removeCategory', categoryId)
        resolve()
      })
    })
  },
  init: ({commit}, templateId: number) => {
    return new Promise<void>(resolve => {
      if (templateId) {
        store.dispatch('degreeEditSession/loadTemplate', templateId).then(resolve)
      } else {
        //TODO: initialize a new template
        commit('resetSession')
        resolve()
      }
    })
  },
  loadTemplate: ({commit}, templateId: number) => {
    return new Promise(resolve => {
      getDegreeTemplate(templateId).then((template: any) => {
        commit('resetSession', template)
        resolve(template)
      })
    })
  },
  setDisableButtons: ({commit}, disable: boolean) => commit('setDisableButtons', disable),
  setEditMode: ({commit}, editMode: string) => commit('setEditMode', editMode),
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
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}
