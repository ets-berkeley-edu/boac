import _ from 'lodash'
import {
  addUnitRequirement,
  getDegreeTemplate,
  updateUnitRequirement
} from '@/api/degree'
import router from '@/router'
import store from '@/store'

const EDIT_MODE_TYPES = ['createUnitRequirement', 'updateUnitRequirement']

const state = {
  degreeName: undefined,
  editMode: undefined,
  templateId: undefined,
  unitRequirements: undefined
}

const getters = {
  degreeName: (state: any): string => state.degreeName,
  editMode: (state: any): string => state.editMode,
  templateId: (state: any): number => state.templateId,
  unitRequirements: (state: any): any[] => state.unitRequirements,
}

const mutations = {
  addUnitRequirement: (state: any, unitRequirement: any) => state.unitRequirements.push(unitRequirement),
  resetSession: (state: any, template: any) => {
    state.editMode = null
    state.templateId = template && template.id
    state.degreeName = template && template.name
    state.unitRequirements = template && template.unitRequirements
  },
  setEditMode(state: any, editMode: string) {
    if (_.isNil(editMode)) {
      state.editMode = null
    } else if (_.find(EDIT_MODE_TYPES, type => editMode.match(type))) {
      // Valid mode
      state.editMode = editMode
    } else {
      throw new TypeError('Invalid page mode: ' + editMode)
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
  loadTemplate: ({commit}, id: number) => {
    return new Promise<void>(resolve => {
      getDegreeTemplate(id).then((template: any) => {
        if (template) {
          commit('resetSession', template)
          resolve()
        } else {
          router.push({path: '/404'})
        }
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
