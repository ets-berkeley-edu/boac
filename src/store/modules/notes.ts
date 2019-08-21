import _ from 'lodash';
import { getTopics } from '@/api/notes';
import { getMyNoteTemplates } from "@/api/note-templates";

const VALID_MODES = ['advanced', 'batch', 'docked', 'editTemplate', 'minimized', 'saving'];

const state = {
  editingNoteId: undefined,
  noteMode: undefined,
  noteTemplates: undefined,
  sid: undefined,
  suggestedTopics: undefined
};

const getters = {
  editingNoteId: (state: any): number => state.editingNoteId,
  noteMode: (state: any): string => state.noteMode,
  noteTemplates: (state: any): any[] => state.noteTemplates,
  sid: (state: any): string => state.sid,
  suggestedTopics: (state: any): any[] => state.suggestedTopics
};

const mutations = {
  editExistingNoteId: (state: any, id: number) => (state.editingNoteId = id),
  endSession: (state: any) => _.each(_.keys(state), key => state[key] = undefined),
  onCreateTemplate: (state: any, template) => {
    state.noteTemplates = _.orderBy(state.noteTemplates.concat([template]), ['title'], ['asc']);
  },
  onDeleteTemplate: (state: any, templateId: any) => {
    let indexOf = state.noteTemplates.findIndex(template => {
      return template.id === templateId;
    });
    state.noteTemplates.splice(indexOf, 1);
  },
  setNoteTemplates: (state: any, templates: any[]) => state.noteTemplates = templates,
  setNoteMode: (state: any, mode: string) => {
    if (_.isNil(mode)) {
      state.noteMode = null;
    } else if (_.find(VALID_MODES, type => mode.match(type))) {
      state.noteMode = mode;
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
  async loadNoteTemplates({ commit, state }) {
    if (_.isUndefined(state.myNoteTemplates)) {
      getMyNoteTemplates().then(templates => commit('setNoteTemplates', templates));
    }
  },
  onCreateTemplate: ({ commit }, template: any) => commit('onCreateTemplate', template),
  onDeleteTemplate: ({ commit }, templateId: number) => commit('onDeleteTemplate', templateId),
  setNoteMode: ({ commit }, mode: string) => {
    if (_.isUndefined(state.suggestedTopics)) {
      // Lazy-load topics
      getTopics(false).then(data => {
        commit('setSuggestedTopics', data);
        commit('setNoteMode', mode);
      });
    } else {
      commit('setNoteMode', mode);
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
