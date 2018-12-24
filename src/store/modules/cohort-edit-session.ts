import _ from 'lodash';
import { getCohort } from '@/api/cohort';
import { getCohortFilterOptions, translateToMenu } from '@/api/menu';

const PAGE_MODES = ['add', 'edit', 'readyForApply', 'readyForSave', 'rename'];

const state = {
  cohortId: undefined,
  cohortName: undefined,
  filters: undefined,
  isCompactView: undefined,
  menu: undefined,
  pageMode: undefined,
  students: undefined,
  totalStudentCount: undefined
};

const getters = {
  cohortId: (state: any): number => state.cohortId,
  cohortName: (state: any): string => state.cohortName,
  filters: (state: any): any[] => state.filters,
  isCompactView: (state: any): boolean => state.isCompactView,
  isOwnedByCurrentUser: (state: any): boolean => state.isOwnedByCurrentUser,
  menu: (state: any): any[] => state.menu,
  pageMode: (state: any) => state.pageMode,
  students: (state: any): any[] => state.students,
  totalStudentCount: (state: any): number => state.totalStudentCount
};

const mutations = {
  addFilter: (state: any, filter: any) => state.filters.push(filter),
  isCompactView: (state: any, compactView: boolean) =>
    (state.isCompactView = compactView),
  setPageMode(state: any, pageMode: string) {
    if (_.includes(PAGE_MODES, pageMode)) {
      state.pageMode = pageMode;
    } else {
      throw new TypeError('Invalid page mode: ' + pageMode);
    }
  },
  removeFilter: (state: any, index: number) => state.filters.splice(index, 1),
  readyForSave: (state: any) => (state.pageMode = 'readyForSave'),
  resetSession: (
    state: any,
    { cohort, filters, students, totalStudentCount }
  ) => {
    state.pageMode = 'readyForSave';
    state.cohortId = cohort && cohort.id;
    state.cohortName = cohort && cohort.name;
    state.isOwnedByCurrentUser = !cohort || cohort.isOwnedByCurrentUser;
    state.filters = filters;
    state.students = students;
    state.totalStudentCount = totalStudentCount;
  },
  toggleCompactView: (state: any) =>
    (state.isCompactView = !state.isCompactView),
  updateMenu: (state: any, menu: any[]) => (state.menu = menu)
};

const actions = {
  init({ commit }, id: number) {
    return new Promise(resolve => {
      commit('setPageMode', 'readyForSave');
      commit('isCompactView', !!id);
      if (id > 0) {
        getCohort(id, true).then(cohort => {
          translateToMenu(cohort.filterCriteria).then(filters => {
            commit('resetSession', {
              cohort,
              filters: filters,
              students: cohort.students,
              totalStudentCount: cohort.totalStudentCount
            });
            getCohortFilterOptions(filters).then(menu => {
              commit('updateMenu', menu);
              resolve();
            });
          });
        });
      } else {
        getCohortFilterOptions([]).then(menu => {
          commit('updateMenu', menu);
          commit('resetSession');
          resolve();
        });
      }
    });
  },
  addFilter: ({ commit, state }, filter: any) => {
    return new Promise(resolve => {
      commit('addFilter', filter);
      getCohortFilterOptions(state.filters).then(menu => {
        commit('updateMenu', menu);
        resolve();
      });
    });
  },
  removeFilter: ({ commit, state }, index: number) => {
    return new Promise(resolve => {
      commit('removeFilter', index);
      getCohortFilterOptions(state.filters).then(menu => {
        commit('updateMenu', menu);
        resolve();
      });
    });
  },
  readyForSave: ({ commit }) => commit('readyForSave'),
  setPageMode: ({ commit }, pageMode: string) =>
    commit('setPageMode', pageMode),
  toggleCompactView: ({ commit }) => commit('toggleCompactView')
};

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
};
