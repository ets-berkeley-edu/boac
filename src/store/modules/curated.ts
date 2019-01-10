import {
  getMyCuratedGroups,
  getStudentsWithAlertsInCohort
} from '@/api/curated';

const state = {
  myCuratedGroups: null
};

const getters = {
  myCuratedGroups: (state: any): any => {
    return state.myCuratedGroups;
  }
};

const mutations = {
  createCuratedGroup: (state: any, group: any) => {
    state.myCuratedGroups.push(group);
  },
  deleteCuratedGroup: (state: any, id: any) => {
    let indexOf = state.myCuratedGroups.findIndex(curatedGroup => {
      return curatedGroup.id === id;
    });
    state.myCuratedGroups.splice(indexOf, 1);
  },
  saveMyCuratedGroups: (state: any, curatedGroups: any) => {
    state.myCuratedGroups = curatedGroups;
  },
  updateCuratedGroup: (state: any, updatedGroup: any) => {
    let group = state.myCuratedGroups.find(
      group => group.id === +updatedGroup.id
    );
    Object.assign(group, updatedGroup);
  }
};

const actions = {
  createCuratedGroup: ({ commit }, group) => {
    commit('createCuratedGroup', group);
  },
  updateCuratedGroup: ({ commit }, group) => {
    commit('updateCuratedGroup', group);
  },
  async loadStudentsWithAlerts({ commit, state }, id) {
    return new Promise(resolve => {
      let curatedGroup = state.myCuratedGroups.find(
        curatedGroup => curatedGroup.id === +id
      );
      if (!curatedGroup.studentsWithAlerts) {
        getStudentsWithAlertsInCohort(id)
          .then(studentsWithAlerts => {
            curatedGroup.studentsWithAlerts = studentsWithAlerts;
            commit('updateCuratedGroup', curatedGroup);
          })
          .then(() => {
            resolve(curatedGroup);
          });
      } else {
        resolve(curatedGroup);
      }
    });
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
