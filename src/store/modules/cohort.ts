import _ from 'lodash';
import { getMyCohorts, getStudentsWithAlerts } from '@/api/cohort';

const state = {
  myCohorts: undefined
};

const getters = {
  myCohorts: (state: any): any => {
    return state.myCohorts;
  }
};

const mutations = {
  addCohort: (state: any, cohort: any) => {
    state.myCohorts.push(cohort);
  },
  deleteCohort: (state: any, id: any) => {
    let indexOf = state.myCohorts.findIndex(cohort => cohort.id === id);
    state.myCohorts.splice(indexOf, 1);
  },
  saveMyCohorts: (state: any, cohorts: any[]) => {
    state.myCohorts = cohorts;
  },
  updateCohort: (state: any, updatedCohort: any) => {
    let cohort = state.myCohorts.find(
      cohort => cohort.id === +updatedCohort.id
    );
    Object.assign(cohort, updatedCohort);
  }
};

const actions = {
  addCohort: ({ commit }, cohort) => {
    commit('addCohort', cohort);
  },
  deleteCohort: ({ commit }, cohort) => {
    commit('deleteCohort', cohort);
  },
  async loadStudentsWithAlerts({ commit, state }, cohortId) {
    return new Promise(resolve => {
      let cohort = state.myCohorts.find(cohort => cohort.id === +cohortId);
      if (!cohort.studentsWithAlerts) {
        getStudentsWithAlerts(cohortId)
          .then(studentsWithAlerts => {
            cohort.studentsWithAlerts = studentsWithAlerts;
            commit('updateCohort', cohort);
          })
          .then(() => {
            resolve(cohort);
          });
      } else {
        resolve(cohort);
      }
    });
  },
  async loadMyCohorts({ commit, state }) {
    if (_.isUndefined(state.myCohorts)) {
      getMyCohorts().then(cohorts => commit('saveMyCohorts', cohorts));
    }
  },
  updateCohort: ({ commit }, cohort) => {
    commit('updateCohort', cohort);
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
