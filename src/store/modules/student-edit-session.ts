import _ from 'lodash';
import { getTopics } from '@/api/notes';

const VALID_MODES = ['advanced', 'batch', 'docked', 'minimized', 'saving'];

const state = {
  editingNoteId: undefined,
  newNoteMode: undefined,
  sid: undefined,
  suggestedTopics: undefined
};

const getters = {
  editingNoteId: (state: any): number => state.editingNoteId,
  newNoteMode: (state: any): string => state.newNoteMode,
  sid: (state: any): string => state.sid,
  suggestedTopics: (state: any): any[] => state.suggestedTopics
};

const mutations = {
  editExistingNoteId: (state: any, id: number) => (state.editingNoteId = id),
  endSession: (state: any) => _.each(_.keys(state), key => state[key] = undefined),
  setNewNoteMode: (state: any, mode: string) => {
    if (_.isNil(mode)) {
      state.newNoteMode = null;
    } else if (_.find(VALID_MODES, type => mode.match(type))) {
      state.newNoteMode = mode;
    } else {
      throw new TypeError('Invalid mode: ' + mode);
    }
  },
  setSid: (state: any, sid: string) => (state.sid = sid),
  setSuggestedTopics: (state: any, topics: any[]) => (state.suggestedTopics = topics)
};

const actions = {
  editExistingNoteId: ({ commit }, id: number) => commit('editExistingNoteId', id),
  endSession: ({ commit }) => commit('endSession'),
  setNewNoteMode: ({ commit }, mode: string) => {
    if (_.isUndefined(state.suggestedTopics)) {
      // Lazy-load topics
      getTopics().then(data => {
        commit('setSuggestedTopics', data);
        commit('setNewNoteMode', mode);
      });
    } else {
      commit('setNewNoteMode', mode);
    }
  },
  setSid: ({ commit }, sid: string) => commit('setSid', sid)
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
