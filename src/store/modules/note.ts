import _ from 'lodash';
import { getMyNoteTemplates } from "@/api/note-templates";
import { getTopics } from '@/api/notes';

const state = {
  noteTemplates: undefined,
  suggestedNoteTopics: undefined
};

const getters = {
  noteTemplates: (state: any): any[] => state.noteTemplates,
  suggestedNoteTopics: (state: any): any[] => state.suggestedNoteTopics
};

const mutations = {
  onCreateTemplate: (state: any, template) => state.noteTemplates = _.orderBy(state.noteTemplates.concat([template]), ['title'], ['asc']),
  onDeleteTemplate: (state: any, templateId: any) => {
    let indexOf = state.noteTemplates.findIndex(template => template.id === templateId);
    state.noteTemplates.splice(indexOf, 1);
  },
  onUpdateTemplate: (state: any, template: any) => {
    let indexOf = state.noteTemplates.findIndex(t => t.id === template.id);
    Object.assign(state.noteTemplates[indexOf], template);
  },
  setNoteTemplates: (state: any, templates: any[]) => state.noteTemplates = templates,
  setSuggestedNoteTopics: (state: any, topics: any[]) => (state.suggestedNoteTopics = topics)
};

const actions = {
  async loadNoteTemplates({ commit, state }) {
    if (_.isUndefined(state.myNoteTemplates)) {
      getMyNoteTemplates().then(templates => commit('setNoteTemplates', templates));
    }
  },
  async loadSuggestedNoteTopics({ commit, state }) {
    if (_.isUndefined(state.suggestedNoteTopics)) {
      getTopics(false).then(data => {
        commit('setSuggestedNoteTopics', data);
      });
    }
  },
  onCreateTemplate: ({ commit }, template: any) => commit('onCreateTemplate', template),
  onDeleteTemplate: ({ commit }, templateId: number) => commit('onDeleteTemplate', templateId),
  onUpdateTemplate: ({ commit }, template: any) => commit('onUpdateTemplate', template)
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
