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

const EDIT_MODE_TYPES = ['add', 'apply', 'edit-[0-9]+', 'rename'];

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
  originalFilters: undefined,
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
  showSortBy(state: any) {
    return !state.isModifiedSinceLastSearch && _.size(state.students) > 1;
  },
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
    if (_.isNil(editMode)) {
      state.editMode = null;
    } else if (_.find(EDIT_MODE_TYPES, type => editMode.match(type))) {
      // Valid mode
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
  restoreOriginalFilters: (state: any) => {
    state.filters = _.cloneDeep(state.originalFilters);
  },
  setCurrentPage: (state: any, currentPage: number) =>
    (state.pagination.currentPage = currentPage),
  setModifiedSinceLastSearch: (state: any, value: boolean) =>
    (state.isModifiedSinceLastSearch = value),
  // Store an unmodified copy of the most recently applied filters in case of cancellation.
  stashOriginalFilters: (state: any) =>
    (state.originalFilters = _.cloneDeep(state.filters)),
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
      commit('setModifiedSinceLastSearch', null);
      store.dispatch('user/setUserPreference', {
        key: 'sortBy',
        value: 'last_name'
      });
      if (id) {
        store.dispatch('cohortEditSession/loadCohort', {
          id: id,
          orderBy: orderBy
        }).then(resolve);
      } else {
        getCohortFilterOptions([]).then(menu => {
          commit('updateMenu', menu);
          commit('resetSession', {});
          commit('stashOriginalFilters');
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
      commit('setModifiedSinceLastSearch', false);
      if (!_.get(state.filters, 'length')) {
        return resolve();
      }
      commit('setEditMode', 'apply');
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
        commit('stashOriginalFilters');
        commit('setEditMode', null);
        resolve();
      });
    });
  },
  createCohort: ({ commit, state }, name: string) => {
    return new Promise(resolve => {
      createCohort(name, state.filters).then(
        cohort => {
          commit('resetSession', {
            cohort,
            filters: state.filters,
            students: state.students,
            totalStudentCount: cohort.totalStudentCount
          });
          commit('stashOriginalFilters');
          commit('setModifiedSinceLastSearch', null);
          resolve();
        }
      );
    });
  },
  loadCohort: ({commit}, {id, orderBy} ) => {
    return new Promise(resolve => {
      getCohort(id, true, orderBy).then(cohort => {
        if (cohort) {
          translateToMenu(cohort.criteria).then(filters => {
            commit('resetSession', {
              cohort,
              filters: filters,
              students: cohort.students,
              totalStudentCount: cohort.totalStudentCount
            });
            commit('stashOriginalFilters');
            getCohortFilterOptions(filters).then(menu => {
              commit('updateMenu', menu);
            });
            resolve();
          });
        } else {
          router.push({ path: '/404' });
        }
      });
    });
  },
  renameCohort: ({ commit, state }, name: string) => {
    return new Promise(resolve => {
      commit('renameCohort', name);
      saveCohort(
        state.cohortId,
        state.cohortName,
        state.filters
      ).then(resolve);
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
  resetFiltersToLastApply: ({ commit, state }) => {
    return new Promise(resolve => {
      commit('restoreOriginalFilters');
      commit('setEditMode', null);
      commit('setModifiedSinceLastSearch', false);
      getCohortFilterOptions(state.filters).then(menu => {
        commit('updateMenu', menu);
        resolve();
      });
    });
  },
  resetFiltersToSaved: ({ commit, state }, cohortId) => {
    commit('setCurrentPage', 0);
    commit('setModifiedSinceLastSearch', null);
    commit('setEditMode', 'apply');
    return new Promise(resolve => {
      store.dispatch('cohortEditSession/loadCohort', {
        id: cohortId,
        orderBy: state.orderBy
      }).then(() => {
        commit('setEditMode', null);
        resolve();
      });
    });
  },
  saveExistingCohort: ({ commit, state }) => {
    return new Promise(resolve => {
      saveCohort(
        state.cohortId,
        state.cohortName,
        state.filters
      ).then(() => {
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
