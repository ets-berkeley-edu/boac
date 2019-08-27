import _ from 'lodash';
import {createNote, createNoteBatch, getDistinctStudentCount} from '@/api/notes';

const VALID_MODES = ['advanced', 'batch', 'docked', 'edit', 'editTemplate', 'minimized', 'saving'];

const state = {
  addedCohorts: [],
  addedCuratedGroups: [],
  attachments: [],
  body: undefined,
  noteMode: undefined,
  objectId: undefined,
  sids: [],
  subject: undefined,
  targetStudentCount: 0,
  topics: []
};

const getters = {
  addedCohorts: (state: any): any[] => state.addedCohorts,
  addedCuratedGroups: (state: any): any[] => state.addedCuratedGroups,
  attachments: (state: any): any[] => state.attachments,
  body: (state: any): string => state.body,
  noteMode: (state: any): string => state.noteMode,
  objectId: (state: any): number => state.objectId,
  sids: (state: any): string[] => state.sids,
  subject: (state: any): string => state.subject,
  targetStudentCount: (state: any): number => state.targetStudentCount,
  topics: (state: any): any[] => state.topics
};

const mutations = {
  addAttachment: (state: any, attachment: any) => (state.attachments.push(attachment)),
  addCohort: (state: any, cohort: any) => state.addedCohorts.push(cohort),
  addCuratedGroup: (state: any, curatedGroup: any) => state.addedCuratedGroups.push(curatedGroup),
  addSid: (state: any, sid: string) => state.sids.push(sid),
  addTopic: (state: any, topic: string) => (state.topics.push(topic)),
  createAdvisingNote: (state: any, isBatchFeature: boolean) => {
    return new Promise(resolve => {
      state.body = _.trim(state.body);
      state.noteMode = 'saving';
      if (isBatchFeature) {
        const addedCohortIds = _.map(state.addedCohorts, 'id');
        const addedCuratedGroupIds = _.map(state.addedCuratedGroups, 'id');
        createNoteBatch(
          state.sids,
          state.subject,
          state.body,
          state.topics,
          state.attachments,
          addedCohortIds,
          addedCuratedGroupIds
        ).then(resolve);
      } else {
        createNote(state.sids[0], state.subject, state.body, state.topics, state.attachments).then(resolve);
      }
    });
  },
  endSession: (state: any) => _.each(_.keys(state), key => state[key] = undefined),
  setObjectId: (state: any, objectId: string[]) => state.objectId = objectId,
  removeAttachment: (state: any, index: number) => (state.attachments.splice(index, 1)),
  removeCohort: (state:any, cohort: any) => state.addedCohorts = _.filter(state.addedCohorts, c => c.id !== cohort.id),
  removeCuratedGroup: (state:any, curatedGroup: any) => (state.addedCuratedGroups = _.filter(state.addedCuratedGroups, c => c.id !== curatedGroup.id)),
  removeStudent: (state:any, sid: string) => (state.sids = _.filter(state.sids, existingSid => existingSid !== sid)),
  removeTopic: (state: any, topic: string) => (state.topics.splice(state.topics.indexOf(topic), 1)),
  clearAllFields: (state: any) => {
    if (state.noteMode === 'batch') {
      state.sids = [];
    }
    state.addedCohorts = [];
    state.addedCuratedGroups = [];
    state.attachments = [];
    state.body = undefined;
    state.subject = undefined;
    state.targetStudentCount = state.sids.length;
    state.topics = [];
  },
  setBody: (state: any, body: string) => (state.body = body),
  setNoteMode: (state: any, mode: string) => {
    if (_.isNil(mode)) {
      state.noteMode = null;
    } else if (_.find(VALID_MODES, type => mode.match(type))) {
      state.noteMode = mode;
    } else {
      throw new TypeError('Invalid mode: ' + mode);
    }
  },
  setSubject: (state: any, subject: string) => (state.subject = subject),
  setTargetStudentCount: (state: any, count: number) => (state.targetStudentCount = count)
};

export function $_notes_recalculateStudentCount({ commit, state }) {
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
}

const actions = {
  addAttachment: ({ commit }, attachment: any) => commit('addAttachment', attachment),
  addCohort: ({commit, state}, cohort: any) => {
    commit('addCohort', cohort);
    $_notes_recalculateStudentCount({ commit, state })
  },
  addCuratedGroup: ({commit, state}, curatedGroup: any) => {
    commit('addCuratedGroup', curatedGroup);
    $_notes_recalculateStudentCount({ commit, state });
  },
  addSid: ({commit, state}, sid: string) => {
    commit('addSid', sid);
    $_notes_recalculateStudentCount({ commit, state });
  },
  addTopic: ({ commit }, topic: string) => commit('addTopic', topic),
  clearAllFields: ({ commit }) => commit('clearAllFields'),
  createAdvisingNote: ({ commit }, isBatchFeature: boolean) => commit('createAdvisingNote', isBatchFeature),
  endSession: ({ commit }) => commit('endSession'),
  onCreateTemplate: ({ commit }, template: any) => commit('onCreateTemplate', template),
  onDeleteTemplate: ({ commit }, templateId: number) => commit('onDeleteTemplate', templateId),
  onUpdateTemplate: ({ commit }, template: any) => commit('onUpdateTemplate', template),
  init: ({ commit }, {note, noteMode, student}) => {
    commit('clearAllFields');
    if (student) {
      commit('addSid', student.sid);
      commit('setTargetStudentCount', 1);
    }
    if (note) {
      commit('setObjectId', note.id);
      commit('setSubject', note.subject);
      commit('setBody', note.body);
      _.each(note.topics, topic => commit('addTopic', topic));
      _.each(note.attachments, attachment => commit('addAttachment', attachment));
    }
    commit('setNoteMode', noteMode);
  },
  recalculateStudentCount: ({commit, state}) => $_notes_recalculateStudentCount({ commit, state }),
  removeAttachment: ({ commit }, index: number) => commit('removeAttachment', index),
  removeCohort: ({commit, state}, cohort: any) => {
    commit('removeCohort', cohort);
    $_notes_recalculateStudentCount({ commit, state })
  },
  removeCuratedGroup: ({commit, state}, curatedGroup: any) => {
    commit('removeCuratedGroup', curatedGroup);
    $_notes_recalculateStudentCount({ commit, state })
  },
  removeStudent: ({commit, state}, sid: string) => {
    commit('removeStudent', sid);
    $_notes_recalculateStudentCount({ commit, state })
  },
  removeTopic: ({ commit }, topic: string) => commit('removeTopic', topic),
  setBody: ({ commit }, body: string) => commit('setBody', body),
  setNoteMode: ({ commit }, noteMode: string) => commit('setNoteMode', noteMode),
  setSubject: ({ commit }, subject: string) => commit('setSubject', subject)
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
