import _ from 'lodash';
import { getCohort, getCohortPerFilters, saveCohort } from '@/api/cohort';
import { getCohortFilterOptions, translateToMenu } from '@/api/menu';
import store from '@/store';

const EDIT_MODE_TYPES = [null, 'add', 'apply', 'edit', 'rename'];

const state = {
  cohortId: undefined,
  cohortName: undefined,
  filters: undefined,
  isCompactView: undefined,
  isModifiedSinceLastSearch: undefined,
  isOwnedByCurrentUser: undefined,
  menu: undefined,
  editMode: undefined,
  students: undefined,
  totalStudentCount: undefined
};

const getters = {
  cohortId: (state: any): number => state.cohortId,
  cohortName: (state: any): string => state.cohortName,
  editMode: (state: any) => state.editMode,
  filters: (state: any): any[] => state.filters,
  isCompactView: (state: any): boolean => state.isCompactView,
  isModifiedSinceLastSearch: (state: any): boolean =>
    state.isModifiedSinceLastSearch,
  isOwnedByCurrentUser: (state: any): boolean => state.isOwnedByCurrentUser,
  menu: (state: any): any[] => state.menu,
  showApplyButton(state: any) {
    return state.isModifiedSinceLastSearch === true && !!_.size(state.filters);
  },
  showSaveButton: (state: any): boolean =>
    state.isModifiedSinceLastSearch === false,
  students: (state: any): any[] => state.students,
  totalStudentCount: (state: any): number => state.totalStudentCount
};

const mutations = {
  addFilter: (state: any, filter: any) => {
    state.filters.push(filter);
    state.isModifiedSinceLastSearch = true;
  },
  isCompactView: (state: any, compactView: boolean) =>
    (state.isCompactView = compactView),
  setEditMode(state: any, editMode: string) {
    if (_.includes(EDIT_MODE_TYPES, editMode)) {
      state.editMode = editMode;
    } else {
      throw new TypeError('Invalid page mode: ' + editMode);
    }
  },
  removeFilter: (state: any, index: number) => {
    state.filters.splice(index, 1);
    state.isModifiedSinceLastSearch = true;
  },
  renameCohort: (state: any, name: string) => (state.cohortName = name),
  resetSession: (
    state: any,
    { cohort, filters, students, totalStudentCount }
  ) => {
    state.editMode = null;
    state.cohortId = cohort && cohort.id;
    state.cohortName = cohort && cohort.name;
    state.isOwnedByCurrentUser = !cohort || cohort.isOwnedByCurrentUser;
    state.filters = filters || [];
    state.students = students;
    state.totalStudentCount = totalStudentCount;
    if (!state.cohortId) {
      // If cohortId is null then show 'Save Cohort' for unsaved search results
      state.isModifiedSinceLastSearch = true;
    }
  },
  toggleCompactView: (state: any) =>
    (state.isCompactView = !state.isCompactView),
  updateMenu: (state: any, menu: any[]) => (state.menu = menu),
  updateStudents: (state: any, { students, totalStudentCount }) => {
    state.students = students;
    state.totalStudentCount = totalStudentCount;
  },
  setModifiedSinceLastSearch: (state: any, value: boolean) =>
    (state.isModifiedSinceLastSearch = value)
};

const actions = {
  init({ commit }, id: number) {
    return new Promise(resolve => {
      commit('setEditMode', null);
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
          commit('resetSession', {});
          resolve();
        });
      }
    });
  },
  addFilter: ({ commit, state }, filter: any) => {
    return new Promise(resolve => {
      commit('addFilter', filter);
      commit('setModifiedSinceLastSearch', true);
      getCohortFilterOptions(state.filters).then(menu => {
        commit('updateMenu', menu);
        resolve();
      });
    });
  },
  applyFilters: ({ commit, state }) => {
    return new Promise(resolve => {
      commit('setEditMode', 'apply');
      getCohortPerFilters(state.filters).then(cohort => {
        commit('updateStudents', {
          students: cohort.students,
          totalStudentCount: cohort.totalStudentCount
        });
        commit('setModifiedSinceLastSearch', false);
        commit('setEditMode', null);
        resolve();
      });
    });
  },
  renameCohort: ({ commit, state }, name: string) => {
    return new Promise(resolve => {
      commit('renameCohort', name);
      saveCohort(state.cohortId, state.cohortName).then(cohort => {
        store.dispatch('cohort/updateCohort', cohort);
        resolve();
      });
    });
  },
  removeFilter: ({ commit, state }, index: number) => {
    return new Promise(resolve => {
      commit('removeFilter', index);
      commit('setModifiedSinceLastSearch', true);
      getCohortFilterOptions(state.filters).then(menu => {
        commit('updateMenu', menu);
        resolve();
      });
    });
  },
  setEditMode: ({ commit }, editMode: string) =>
    commit('setEditMode', editMode),
  toggleCompactView: ({ commit }) => commit('toggleCompactView')
};

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
};
