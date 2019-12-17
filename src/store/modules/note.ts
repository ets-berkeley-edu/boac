import _ from 'lodash';
import { getMyNoteTemplates } from "@/api/note-templates";

const state = {
  noteTemplates: undefined
};

const getters = {
  noteTemplates: (state: any): any[] => state.noteTemplates
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
  setNoteTemplates: (state: any, templates: any[]) => state.noteTemplates = templates
};

const actions = {
  async loadNoteTemplates({ commit, state }) {
    if (_.isUndefined(state.myNoteTemplates)) {
      getMyNoteTemplates().then(templates => commit('setNoteTemplates', templates));
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
