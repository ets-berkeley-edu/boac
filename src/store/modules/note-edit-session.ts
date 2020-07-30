import _ from 'lodash';
import {createNote, createNoteBatch, getDistinctStudentCount} from '@/api/notes';
import { getMyNoteTemplates } from "@/api/note-templates";

const VALID_MODES = ['batch', 'create', 'edit', 'editTemplate'];

const $_getDefaultModel = () => {
  return {
    id: undefined,
    subject: undefined,
    body: undefined,
    topics: [],
    attachments: [],
    deleteAttachmentIds: []
  };
};

const $_recalculateStudentCount = ({ commit, state }) => {
  const cohortIds = _.map(state.addedCohorts, 'id');
  const curatedGroupIds = _.map(state.addedCuratedGroups, 'id');
  const sids = state.sids;
  if (cohortIds.length || curatedGroupIds.length) {
    getDistinctStudentCount(sids, cohortIds, curatedGroupIds).then(function(data) {
      commit('setTargetStudentCount', data.count);
    });
  } else {
    commit('setTargetStudentCount', sids.length);
  }
};

const state = {
  addedCohorts: [],
  addedCuratedGroups: [],
  isFocusLockDisabled: undefined,
  isSaving: false,
  mode: undefined,
  model: $_getDefaultModel(),
  noteTemplates: undefined,
  sids: [],
  targetStudentCount: 0
};

const getters = {
  addedCohorts: (state: any): any[] => state.addedCohorts,
  addedCuratedGroups: (state: any): any[] => state.addedCuratedGroups,
  disableNewNoteButton: (state: any): boolean => !!state.mode,
  isFocusLockDisabled: (state: any): boolean => state.isFocusLockDisabled,
  isSaving: (state: any): boolean => state.isSaving,
  mode: (state: any): string => state.mode,
  model: (state: any): any => state.model,
  noteTemplates: (state: any): any[] => state.noteTemplates,
  sids: (state: any): string[] => state.sids,
  targetStudentCount: (state: any): number => state.targetStudentCount,
  template: (state: any): any => state.template
};

const mutations = {
  addAttachment: (state: any, attachment: any) => (state.model.attachments.push(attachment)),
  addCohort: (state: any, cohort: any) => state.addedCohorts.push(cohort),
  addCuratedGroup: (state: any, curatedGroup: any) => state.addedCuratedGroups.push(curatedGroup),
  addSid: (state: any, sid: string) => state.sids.push(sid),
  addTopic: (state: any, topic: string) => (state.model.topics.push(topic)),
  exitSession: (state: any) => {
    state.addedCohorts = [];
    state.addedCuratedGroups = [];
    state.isSaving = false;
    state.mode = undefined;
    state.model = $_getDefaultModel();
    state.sids = [];
    state.targetStudentCount = 0;
  },
  onCreateTemplate: (state: any, template) => state.noteTemplates = _.orderBy(state.noteTemplates.concat([template]), ['title'], ['asc']),
  onDeleteTemplate: (state: any, templateId: any) => {
    const indexOf = state.noteTemplates.findIndex(template => template.id === templateId);
    state.noteTemplates.splice(indexOf, 1);
  },
  onUpdateTemplate: (state: any, template: any) => {
    const indexOf = state.noteTemplates.findIndex(t => t.id === template.id);
    Object.assign(state.noteTemplates[indexOf], template);
  },
  removeAttachment: (state: any, index: number) => {
    const attachment = state.model.attachments[index];
    if (attachment.id) {
      state.model.deleteAttachmentIds.push(attachment.id);
    }
    state.model.attachments.splice(index, 1);
  },
  removeCohort: (state:any, cohort: any) => state.addedCohorts = _.filter(state.addedCohorts, c => c.id !== cohort.id),
  removeCuratedGroup: (state:any, curatedGroup: any) => (state.addedCuratedGroups = _.filter(state.addedCuratedGroups, c => c.id !== curatedGroup.id)),
  removeStudent: (state:any, sid: string) => (state.sids = _.filter(state.sids, existingSid => existingSid !== sid)),
  removeTopic: (state: any, topic: string) => (state.model.topics.splice(state.model.topics.indexOf(topic), 1)),
  setBody: (state: any, body: string) => (state.model.body = body),
  setFocusLockDisabled: (state: any, isDisabled: boolean) => (state.isFocusLockDisabled = isDisabled),
  setIsSaving: (state: any, isSaving: boolean) => (state.isSaving = isSaving),
  setMode: (state: any, mode: string) => {
    if (_.isNil(mode)) {
      state.mode = undefined;
    } else if (_.find(VALID_MODES, type => mode.match(type))) {
      state.mode = mode;
    } else {
      throw new TypeError('Invalid mode: ' + mode);
    }
  },
  setModel: (state: any, model: any) => {
    if (model) {
      state.model = {
        id: model.id,
        subject: model.subject,
        body: model.body,
        topics: model.topics || [],
        attachments: model.attachments || [],
        deleteAttachmentIds: []
      };
    } else {
      state.model = $_getDefaultModel();
    }
  },
  setNoteTemplates: (state: any, templates: any[]) => state.noteTemplates = templates,
  setSubject: (state: any, subject: string) => (state.model.subject = subject),
  setTargetStudentCount: (state: any, count: number) => (state.targetStudentCount = count)
};

const actions = {
  addAttachment: ({ commit }, attachment: any) => commit('addAttachment', attachment),
  addCohort: ({commit, state}, cohort: any) => {
    commit('addCohort', cohort);
    $_recalculateStudentCount({ commit, state })
  },
  addCuratedGroup: ({commit, state}, curatedGroup: any) => {
    commit('addCuratedGroup', curatedGroup);
    $_recalculateStudentCount({ commit, state });
  },
  addSid: ({commit, state}, sid: string) => {
    commit('addSid', sid);
    $_recalculateStudentCount({ commit, state });
  },
  addTopic: ({ commit }, topic: string) => commit('addTopic', topic),
  createAdvisingNote: ({commit, state}, isBatchFeature: boolean) => {
    return new Promise(resolve => {
      commit('setBody', _.trim(state.model.body));
      const [templateAttachments, attachments] = state.model.attachments.reduce((result, a) => {
        result[a.noteTemplateId ? 0 : 1].push(a);
        return result;
      }, [[], []]);
      if (isBatchFeature) {
        const cohortIds = _.map(state.addedCohorts, 'id');
        const curatedGroupIds = _.map(state.addedCuratedGroups, 'id');
        createNoteBatch(
          state.sids,
          state.model.subject,
          state.model.body,
          state.model.topics,
          attachments,
          _.map(templateAttachments, 'id'),
          cohortIds,
          curatedGroupIds
        ).then(resolve);
      } else {
        createNote(
            state.sids[0],
            state.model.subject,
            state.model.body,
            state.model.topics,
            attachments,
            _.map(templateAttachments, 'id'),
        ).then(resolve);
      }
    });
  },
  exitSession: ({ commit }) => commit('exitSession'),
  async loadNoteTemplates({ commit, state }) {
    if (_.isUndefined(state.myNoteTemplates)) {
      getMyNoteTemplates().then(templates => commit('setNoteTemplates', templates));
    }
  },
  onCreateTemplate: ({ commit }, template: any) => commit('onCreateTemplate', template),
  onDeleteTemplate: ({ commit }, templateId: number) => commit('onDeleteTemplate', templateId),
  onUpdateTemplate: ({ commit }, template: any) => commit('onUpdateTemplate', template),
  removeAttachment: ({ commit }, index: number) => commit('removeAttachment', index),
  removeCohort: ({commit, state}, cohort: any) => {
    commit('removeCohort', cohort);
    $_recalculateStudentCount({ commit, state })
  },
  removeCuratedGroup: ({commit, state}, curatedGroup: any) => {
    commit('removeCuratedGroup', curatedGroup);
    $_recalculateStudentCount({ commit, state })
  },
  removeStudent: ({commit, state}, sid: string) => {
    commit('removeStudent', sid);
    $_recalculateStudentCount({ commit, state })
  },
  removeTopic: ({ commit }, topic: string) => commit('removeTopic', topic),
  resetModel: ({ commit }) => commit('setModel', $_getDefaultModel()),
  setBody: ({ commit }, body: string) => commit('setBody', body),
  setFocusLockDisabled: ({ commit }, isDisabled: boolean) => commit('setFocusLockDisabled', isDisabled),
  setIsSaving: ({ commit }, isSaving: boolean) => commit('setIsSaving', isSaving),
  setMode: ({ commit }, mode: string) => commit('setMode', mode),
  setModel: ({ commit }, model?: any) => commit('setModel', model),
  setSubject: ({ commit }, subject: string) => commit('setSubject', subject)
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
