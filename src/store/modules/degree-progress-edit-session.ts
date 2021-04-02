import router from '@/router'
import store from '@/store'

function getTemplate(id: number) {
  //TODO: replace with API call
  return new Promise(resolve => {
    const template = {
      name: 'Bioengineering 2019',
      createdAt: '2019-07-18',
      id: id,
      requirementCategories: [],
      unitRequirements: [
        {
          id: 1,
          templateId: id,
          name: 'Engineering Requirements',
          minUnits: 45
        }
      ]
    }
    resolve(template)
  })
}

function saveUnitRequirements(templateId: number, unitRequirements: any) {
  //TODO: replace with API call
  return new Promise(resolve => {
    resolve(unitRequirements)
  })
}

const state = {
  degreeName: undefined,
  templateId: undefined,
  unitRequirements: undefined
}

const getters = {
  degreeName: (state: any): string => state.degreeName,
  templateId: (state: any): number => state.templateId,
  unitRequirements: (state: any): number => state.unitRequirements,
}

const mutations = {
  addUnitRequirement: (state: any, unitRequirement: any) => state.unitRequirements.push(unitRequirement),
  resetSession: (state: any, template: any) => {
    state.templateId = template && template.id
    state.degreeName = template && template.name
    state.unitRequirements = template && template.unitRequirements
  }
}

const actions = {
  addUnitRequirement: (commit, unitRequirement: any) => commit('addUnitRequirement', unitRequirement),
  init: ({commit}, templateId: number) => {
    return new Promise<void>(resolve => {
      if (templateId) {
        store.dispatch('degreeProgressEditSession/loadTemplate', {id: templateId}).then(resolve)
      } else {
        //TODO: initialize a new template
        commit('resetSession')
        resolve()
      }
    })
  },
  loadTemplate: ({commit}, id: number) => {
    return new Promise<void>(resolve => {
      getTemplate(id).then((template: any) => {
        if (template) {
          commit('resetSession', template)
          resolve()
        } else {
          router.push({path: '/404'})
        }
      })
    })
  },
  saveUnitRequirements: (state) => {
    return new Promise(resolve => {
      saveUnitRequirements(state.templateId, state.unitRequirements).then(resolve)
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
