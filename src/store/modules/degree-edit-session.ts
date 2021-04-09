import _ from 'lodash'
import {
  addUnitRequirement,
  getDegreeTemplate,
  updateUnitRequirement
} from '@/api/degree'
import store from '@/store'

const EDIT_MODE_TYPES = ['createUnitRequirement', 'updateUnitRequirement']

const state = {
  categories: undefined,
  degreeName: undefined,
  editMode: undefined,
  templateId: undefined,
  unitRequirements: undefined
}

const getters = {
  categories: (state: any): any[] => state.categories,
  degreeName: (state: any): string => state.degreeName,
  editMode: (state: any): string => state.editMode,
  templateId: (state: any): number => state.templateId,
  unitRequirements: (state: any): any[] => state.unitRequirements,
}

const mutations = {
  addUnitRequirement: (state: any, unitRequirement: any) => state.unitRequirements.push(unitRequirement),
  resetSession: (state: any, template: any) => {
    state.editMode = null
    state.categories = template && template.categories
    state.degreeName = template && template.name
    state.templateId = template && template.id
    state.unitRequirements = template && template.unitRequirements
  },
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
