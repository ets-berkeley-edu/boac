// -----
// TODO: The cohort object in the store will have two elements: cohort and filterRowEditSession.
//       The latter is non null when a filter is being added or edited, before it is saved.
//       The component with Apply/Save buttons will watch filterRowEditSession and show/hide appropriately.
// -----
// TODO: Each button on UI has a state in store. Components for events at the store, depending on the event.
//       Then, have a mixin with one getter per state entry
// -----
// TODO: When a new filter row is added, send the set of selected filters to the server side
//       in order to get up to date menu options, with proper disabling of
//       certain options (primary and secondary)
// -----
// TODO: The base64 and menus are returned to client in one response. When user clicks Apply the client
//       side just posts the base64 hash to server where it is decoded and used to create student query.
//       These same steps happen when a filter criteria row is removed on the client side.
// -----

import _ from 'lodash';
import { getCohort, translateFilterCriteria } from '@/api/cohort';

const state = {
  id: undefined,
  isOwnedByCurrentUser: undefined,
  name: undefined,
  filters: undefined,
  students: undefined,
  totalStudentCount: undefined
};

const getters = {
  id: (state: any): any => state.id,
  isOwnedByCurrentUser: (state: any): any => state.isOwnedByCurrentUser,
  name: (state: any): any => state.name,
  filters: (state: any): any => state.filters,
  students: (state: any): any => state.students,
  totalStudentCount: (state: any): any => state.totalStudentCount
};

const mutations = {
  resetSession: (state: any, cohort: any) => {
    state.id = _.get(cohort, 'id');
    state.isOwnedByCurrentUser = _.get(cohort, 'isOwnedByCurrentUser');
    state.name = _.get(cohort, 'name');
    state.filters = _.get(cohort, 'filters');
    state.students = _.get(cohort, 'students');
    state.totalStudentCount = _.get(cohort, 'totalStudentCount');
  },
  removeFilter: (state: any, filter: any) => {
    state.filters = _.remove(state.filters, existingFilter => {
      // TODO: fix the following comparison such that we remove the proper filter
      return filter === existingFilter;
    });
  }
};

const actions = {
  init({ commit }, id: number) {
    return new Promise(resolve => {
      if (id > 0) {
        getCohort(id, true).then(cohort => {
          translateFilterCriteria(cohort.filterCriteria).then(filters => {
            cohort.filters = filters;
            commit('resetSession', cohort);
            resolve();
          });
        });
      } else {
        commit('resetSession');
        resolve();
      }
    });
  },
  removeFilter({ commit }, filter: any) {
    commit('removeFilter', filter);
  }
};

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
};
