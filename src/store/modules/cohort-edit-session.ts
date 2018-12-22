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
  cohort: {
    id: undefined,
    isOwnedByCurrentUser: undefined,
    name: undefined,
    filters: undefined,
    students: undefined,
    totalStudentCount: undefined
  },
  modes: {
    rename: false,
    searching: false,
    showFilters: false
  }
};

const getters = {
  cohortId: (state: any): number => state.cohort.id,
  isOwnedByCurrentUser: (state: any): boolean =>
    state.cohort.isOwnedByCurrentUser,
  cohortName: (state: any): string => state.cohort.name,
  filters: (state: any): any[] => state.cohort.filters,
  students: (state: any): any[] => state.cohort.students,
  totalStudentCount: (state: any): number => state.cohort.totalStudentCount,
  renameMode: (state: any): boolean => state.modes.rename,
  searchingMode: (state: any): boolean => state.modes.searching,
  showFiltersMode: (state: any): boolean => state.modes.showFilters
};

const mutations = {
  resetSession: (state: any, cohort: any) => {
    state.cohort.id = _.get(cohort, 'id');
    state.cohort.isOwnedByCurrentUser = _.get(cohort, 'isOwnedByCurrentUser');
    state.cohort.name = _.get(cohort, 'name');
    state.cohort.filters = _.get(cohort, 'filters');
    state.cohort.students = _.get(cohort, 'students');
    state.cohort.totalStudentCount = _.get(cohort, 'totalStudentCount');
  },
  removeFilter: (state: any, index: number) =>
    state.cohort.filters.splice(index, 1),
  toggleShowFilters: (state: any) =>
    (state.modes.showFilters = !state.modes.showFilters),
  toggleRenameMode: (state: any) => (state.modes.rename = !state.modes.rename)
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
  removeFilter: ({ commit }, index: number) => commit('removeFilter', index),
  toggleShowFilters: ({ commit }) => commit('toggleShowFilters'),
  toggleRenameMode: ({ commit }) => commit('toggleRenameMode')
};

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
};
