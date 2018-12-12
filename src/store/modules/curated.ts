import { getMyCuratedGroups } from '@/api/curated';

const state = {
  myCuratedGroups: null
};

const getters = {
  myCuratedGroups: (state: any): any => {
    return state.myCuratedGroups;
  }
};

const mutations = {
  createdCuratedGroup: (state: any, group: any) => {
    state.myCuratedGroups.push(group);
  },
  saveMyCuratedGroups: (state: any, curatedGroups: any) => {
    state.myCuratedGroups = curatedGroups;
  },
  updateCuratedGroup: (state: any, updatedGroup: any) => {
    let group = state.myCuratedGroups.find(
      group => group.id === +updatedGroup.id
    );
    group.name = updatedGroup.name;
    group.studentCount = updatedGroup.studentCount;
    group.students = updatedGroup.students;
  }
};

const actions = {
  createdCuratedGroup: ({ commit }, group) => {
    commit('createdCuratedGroup', group);
  },
  updateCuratedGroup: ({ commit }, group) => {
    commit('updateCuratedGroup', group);
  },
  async loadMyCuratedGroups({ commit, state }) {
    if (state.myCuratedGroups === null) {
      getMyCuratedGroups().then(curatedGroups => {
        commit('saveMyCuratedGroups', curatedGroups);
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
