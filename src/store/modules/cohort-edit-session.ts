import _ from 'lodash';
import {
  createCohort,
  getCohort,
  getStudentsPerFilters,
  saveCohort
} from '@/api/cohort';
import { getCohortFilterOptions, translateToMenu } from '@/api/menu';
import router from '@/router';
import store from '@/store';

const EDIT_MODE_TYPES = [null, 'add', 'apply', 'edit', 'rename'];

const state = {
  cohortId: undefined,
  cohortName: undefined,
  editMode: undefined,
  filters: undefined,
  isCompactView: undefined,
  isModifiedSinceLastSearch: undefined,
  isOwnedByCurrentUser: undefined,
  menu: undefined,
  orderBy: undefined,
  pagination: {
    currentPage: undefined,
    itemsPerPage: 50
  },
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
  pagination: (state: any) => state.pagination,
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
    state.pagination.currentPage = 1;
    if (!state.cohortId) {
      // If cohortId is null then show 'Save Cohort' for unsaved search results
      state.isModifiedSinceLastSearch = true;
    }
  },
  setCurrentPage: (state: any, currentPage: number) =>
    (state.pagination.currentPage = currentPage),
  setModifiedSinceLastSearch: (state: any, value: boolean) =>
    (state.isModifiedSinceLastSearch = value),
  toggleCompactView: (state: any) =>
    (state.isCompactView = !state.isCompactView),
  updateMenu: (state: any, menu: any[]) => (state.menu = menu),
  updateStudents: (state: any, { students, totalStudentCount }) => {
    state.students = students;
    state.totalStudentCount = totalStudentCount;
  },
  updateExistingFilter: (state: any, { index, updatedFilter }) => {
    state.filters[index] = updatedFilter;
    state.isModifiedSinceLastSearch = true;
  }
};

const actions = {
  init({ commit }, { id, orderBy }) {
    return new Promise(resolve => {
      commit('setEditMode', null);
      commit('isCompactView', !!id);
      commit('setCurrentPage', 0);
      store.dispatch('user/setUserPreference', {
        key: 'sortBy',
        value: 'last_name'
      });
      if (id > 0) {
        getCohort(id, true, orderBy).then(cohort => {
          if (cohort) {
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
          } else {
            router.push({ path: '/404' });
          }
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
  applyFilters: ({ commit, state }, orderBy) => {
    return new Promise(resolve => {
      commit('setEditMode', 'apply');
      commit('setModifiedSinceLastSearch', false);
      let offset =
        (state.pagination.currentPage - 1) * state.pagination.itemsPerPage;
      getStudentsPerFilters(
        state.filters,
        orderBy,
        offset,
        state.pagination.itemsPerPage
      ).then(data => {
        commit('updateStudents', {
          students: data.students,
          totalStudentCount: data.totalStudentCount
        });
        commit('setEditMode', null);
        resolve();
      });
    });
  },
  createCohort: ({ commit, state }, name: string) => {
    return new Promise(resolve => {
      createCohort(name, state.filters, state.totalStudentCount).then(
        cohort => {
          store.dispatch('cohort/addCohort', cohort);
          commit('resetSession', {
            cohort,
            filters: state.filters,
            students: state.students,
            totalStudentCount: cohort.totalStudentCount
          });
          commit('setModifiedSinceLastSearch', null);
          resolve();
        }
      );
    });
  },
  renameCohort: ({ commit, state }, name: string) => {
    return new Promise(resolve => {
      commit('renameCohort', name);
      saveCohort(
        state.cohortId,
        state.cohortName,
        state.filters,
        state.totalStudentCount
      ).then(cohort => {
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
  saveExistingCohort: ({ commit, state }) => {
    return new Promise(resolve => {
      saveCohort(
        state.cohortId,
        state.cohortName,
        state.filters,
        state.totalStudentCount
      ).then(cohort => {
        store.dispatch('cohort/updateCohort', cohort);
        commit('setModifiedSinceLastSearch', null);
        resolve();
      });
    });
  },
  setCurrentPage: ({ commit }, currentPage: number) =>
    commit('setCurrentPage', currentPage),
  setEditMode: ({ commit }, editMode: string) =>
    commit('setEditMode', editMode),
  updateExistingFilter: ({ commit, state }, { index, updatedFilter }: any) => {
    return new Promise(resolve => {
      commit('updateExistingFilter', { index, updatedFilter });
      commit('setModifiedSinceLastSearch', true);
      getCohortFilterOptions(state.filters).then(menu => {
        commit('updateMenu', menu);
        resolve();
      });
    });
  },
  toggleCompactView: ({ commit }) => commit('toggleCompactView')
};

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
};
