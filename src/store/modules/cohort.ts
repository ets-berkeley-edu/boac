import { getMyCohorts } from '@/api/cohort';

const state = {
  myCohorts: null
};

const getters = {
  myCohorts: (state: any): any => {
    return state.myCohorts;
  }
};

const mutations = {
  saveMyCohorts: (state: any, cohorts: any) => {
    state.myCohorts = cohorts;
  }
};

const actions = {
  async loadMyCohorts({ commit, state }) {
    if (state.myCohorts === null) {
      getMyCohorts().then(cohorts => {
        commit('saveMyCohorts', cohorts);
      });
    }
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
