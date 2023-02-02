import _ from 'lodash'
import Vue from 'vue'
import {getAllTopics} from '@/api/topics'
import {getMySearchHistory} from '@/api/search'

const state = {
  domain: undefined,
  includeAdmits: undefined,
  includeCourses: undefined,
  includeNotes: undefined,
  includeStudents: undefined,
  queryText: undefined,
  searchHistory: [],
  topicOptions: []
}

const getters = {
  domain: (state: any): string[] => state.domain,
  includeAdmits: (state: any): boolean => state.includeAdmits,
  includeCourses: (state: any): boolean => state.includeCourses,
  includeNotes: (state: any): boolean => state.includeNotes,
  includeStudents: (state: any): boolean => state.includeStudents,
  queryText: (state: any): string => state.queryText,
  topicOptions: (state: any): string[] => state.topicOptions
}

const mutations = {
  resetAdvancedSearch: (state: any) => {
    const currentUser = Vue.prototype.$currentUser
    const domain = ['students']
    if (currentUser.canAccessCanvasData) {
      domain.push('courses')
    }
    if (currentUser.canAccessAdvisingData) {
      domain.push('notes')
    }
    if (currentUser.canAccessAdmittedStudents) {
      domain.push('admits')
    }
    state.domain = domain
    state.includeAdmits = domain.includes('admits')
    state.includeCourses = domain.includes('courses')
    state.includeNotes = domain.includes('notes')
    state.includeStudents = domain.includes('students')
  },
  setDomain: (state: any, domain: string) => state.domain = domain,
  setIncludeAdmits: (state: any, value: boolean) => state.includeAdmits = value,
  setIncludeCourses: (state: any, value: boolean) => state.includeCourses = value,
  setIncludeNotes: (state: any, value: boolean) => state.includeNotes = value,
  setIncludeStudents: (state: any, value: boolean) => state.includeStudents = value,
  setSearchHistory: (state: any, searchHistory: any[]) => state.searchHistory = searchHistory,
  setTopicOptions: (state: any, topicOptions: any[]) => state.topicOptions = topicOptions,
  setQueryText: (state: any, queryText: string) => state.queryText = queryText
}

const actions = {
  init: ({commit}) => {
    return new Promise<void>(resolve => {
      commit('resetAdvancedSearch')

      getAllTopics(true).then(rows => {
        const topicOptions: any[] = []
        _.each(rows, row => {
          const topic = row['topic']
          topicOptions.push({
            text: topic,
            value: topic
          })
        })
        commit('setTopicOptions', topicOptions)
        getMySearchHistory().then(history => {
          commit('setSearchHistory', history)
          return resolve()
        })
      })
    })
  },
  resetAdvancedSearch: ({commit}) => commit('resetAdvancedSearch'),
  setIncludeAdmits: ({commit}, value: boolean) => commit('setIncludeAdmits', value),
  setIncludeCourses: ({commit}, value: boolean) => commit('setIncludeCourses', value),
  setIncludeNotes: ({commit}, value: boolean) => commit('setIncludeNotes', value),
  setIncludeStudents: ({commit}, value: boolean) => commit('setIncludeStudents', value),
  setQueryText: ({commit}, data) => commit('setQueryText', data),
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
