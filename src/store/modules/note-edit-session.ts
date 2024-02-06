import _ from 'lodash'
import moment from 'moment'
import {alertScreenReader} from '@/store/modules/context'
import {applyNoteTemplate, deleteNote, removeAttachment, updateNote} from '@/api/notes'
import {getDistinctSids} from '@/api/student'
import {getMyNoteTemplates} from '@/api/note-templates'
import {isAutoSaveMode} from '@/store/utils/note'

const VALID_MODES = ['createBatch', 'createNote', 'editDraft', 'editNote', 'editTemplate']

type Model = {
  id: number;
  subject?: string;
  body?: string;
  contactType?: string;
  isDraft?: boolean;
  isPrivate?: boolean;
  setDate?: any;
  topics?: string[];
  attachments?: string[];
  deleteAttachmentIds?: number[];
}

const $_addSid = ({commit, state}, sid: string) => {
  const sids = state.sids.concat(sid)
  $_recalculateStudentCount(sids, state.addedCohorts, state.addedCuratedGroups).then(sids => {
    commit('addSid', sid)
    commit('setCompleteSidSet', sids)
  }).finally(() => commit('setIsRecalculating', false))
}

function $_getDefaultModel():Model {
  return {
    id: NaN,
    subject: undefined,
    body: undefined,
    contactType: undefined,
    isDraft: undefined,
    isPrivate: undefined,
    setDate: undefined,
    topics: [],
    attachments: [],
    deleteAttachmentIds: []
  }
}

const $_recalculateStudentCount = (sids, cohorts, curatedGroups) => {
  return new Promise(resolve => {
    const cohortIds = _.map(cohorts, 'id')
    const curatedGroupIds = _.map(curatedGroups, 'id')
    if (cohortIds.length || curatedGroupIds.length) {
      getDistinctSids(sids, cohortIds, curatedGroupIds).then(data => resolve(data.sids))
    } else {
      resolve(sids)
    }
  })
}

const $_updateAdvisingNote = ({commit, state}) => {
  return new Promise(resolve => {
    commit('setBody', _.trim(state.model.body))
    const setDate = state.model.setDate ? state.model.setDate.format('YYYY-MM-DD') : null
    const sids: string[] = Array.from(state.completeSidSet)
    const isDraft = state.model.isDraft
    updateNote(
      state.model.id,
      state.model.body,
      _.map(state.addedCohorts, 'id'),
      state.model.contactType,
      _.map(state.addedCuratedGroups, 'id'),
      isDraft,
      state.model.isPrivate,
      setDate,
      sids,
      state.model.subject,
      [],
      state.model.topics
    ).then(resolve)
  })
}

const state = {
  addedCohorts: [],
  addedCuratedGroups: [],
  autoSaveJob: undefined,
  boaSessionExpired: false,
  completeSidSet: new Set(),
  isFocusLockDisabled: undefined,
  isAutoSavingDraftNote: false,
  isSaving: false,
  isRecalculating: false,
  mode: undefined,
  model: $_getDefaultModel(),
  noteTemplates: undefined,
  originalModel: undefined,
  sids: []
}

const getters = {
  addedCohorts: (state: any): any[] => state.addedCohorts,
  addedCuratedGroups: (state: any): any[] => state.addedCuratedGroups,
  autoSaveJob: (state: any): any => state.autoSaveJob,
  boaSessionExpired: (state: any): any[] => state.boaSessionExpired,
  disableNewNoteButton: (state: any): boolean => !!state.mode,
  isAutoSavingDraftNote: (state: any): boolean => state.isAutoSavingDraftNote,
  isFocusLockDisabled: (state: any): boolean => state.isFocusLockDisabled,
  isSaving: (state: any): boolean => state.isSaving,
  isRecalculating: (state: any): boolean => state.isRecalculating,
  mode: (state: any): string => state.mode,
  model: (state: any): any => state.model,
  noteTemplates: (state: any): any[] => state.noteTemplates,
  sids: (state: any): string[] => state.sids,
  completeSidSet: (state: any): number[] => Array.from(state.completeSidSet),
  template: (state: any): any => state.template
}

const mutations = {
  addAttachments: (state: any, attachments: any[]) => state.model.attachments = _.sortBy(attachments, ['name', 'id']),
  addCohort: (state: any, cohort: any) => state.addedCohorts.push(cohort),
  addCuratedGroup: (state: any, curatedGroup: any) => state.addedCuratedGroups.push(curatedGroup),
  addSid: (state: any, sid: string) => state.sids.push(sid),
  addSidList: (state: any, sidList: string[]) => (state.sids = state.sids.concat(sidList)),
  addTopic: (state: any, topic: string) => (state.model.topics.push(topic)),
  exitSession: (state: any) => {
    clearTimeout(state.autoSaveJob)
    state.autoSaveJob = null
    state.addedCohorts = []
    state.addedCuratedGroups = []
    state.completeSidSet = new Set()
    state.isSaving = false
    state.mode = undefined
    state.model = $_getDefaultModel()
    state.originalModel = _.cloneDeep(state.model)
    state.sids = []
  },
  isAutoSavingDraftNote: (state: any, value: boolean) => state.isAutoSavingDraftNote = value,
  onBoaSessionExpires: (state: any) => state.boaSessionExpired = true,
  onUpdateTemplate: (state: any, template: any) => {
    const indexOf = state.noteTemplates.findIndex(t => t.id === template.id)
    Object.assign(state.noteTemplates[indexOf], template)
  },
  removeAllStudents: (state: any) => state.sids = [],
  removeAttachment: (state: any, index: number) => {
    const attachment = state.model.attachments[index]
    if (attachment.id) {
      state.model.deleteAttachmentIds.push(attachment.id)
    }
    state.model.attachments.splice(index, 1)
  },
  removeCohort: (state:any, cohort: any) => state.addedCohorts = _.filter(state.addedCohorts, c => c.id !== cohort.id),
  removeCuratedGroup: (state:any, curatedGroup: any) => (state.addedCuratedGroups = _.filter(state.addedCuratedGroups, c => c.id !== curatedGroup.id)),
  removeStudent: (state:any, sid: string) => (state.sids = _.filter(state.sids, existingSid => existingSid !== sid)),
  removeTopic: (state: any, topic: string) => (state.model.topics.splice(state.model.topics.indexOf(topic), 1)),
  setAutoSaveJob: (state: any, jobId: number) => state.autoSaveJob = jobId,
  setBody: (state: any, body: string) => (state.model.body = body),
  setCompleteSidSet: (state: any, completeSidSet: number[]) => state.completeSidSet = new Set(completeSidSet),
  setContactType: (state: any, contactType: string) => (state.model.contactType = contactType),
  setFocusLockDisabled: (state: any, isDisabled: boolean) => (state.isFocusLockDisabled = isDisabled),
  setIsSaving: (state: any, isSaving: boolean) => (state.isSaving = isSaving),
  setIsRecalculating: (state: any, isRecalculating: boolean) => (state.isRecalculating = isRecalculating),
  setMode: (state: any, mode: string) => {
    if (_.isNil(mode)) {
      state.mode = undefined
    } else if (_.find(VALID_MODES, type => mode.match(type))) {
      state.mode = mode
    } else {
      throw new TypeError('Invalid mode: ' + mode)
    }
  },
  setModelId: (state: any, modelId: number) => state.model.id = modelId,
  setModel: (state: any, note?: any) => {
    if (note) {
      const model = _.cloneDeep(note)
      state.model = {
        attachments: model.attachments || [],
        body: model.body,
        contactType: model.contactType || null,
        deleteAttachmentIds: [],
        id: model.id,
        isDraft: model.isDraft,
        isPrivate: model.isPrivate,
        setDate: model.setDate ? moment(model.setDate) : null,
        subject: model.subject,
        topics: model.topics || [],
      }
    } else {
      state.model = $_getDefaultModel()
    }
    state.originalModel = _.cloneDeep(state.model)
  },
  setNoteTemplates: (state: any, templates: any[]) => state.noteTemplates = templates,
  setIsDraft: (state: any, isDraft: boolean) => (state.model.isDraft = isDraft),
  setIsPrivate: (state: any, isPrivate: boolean) => (state.model.isPrivate = isPrivate),
  setSetDate: (state: any, setDate: any) => (state.model.setDate = setDate ? moment(setDate) : null),
  setSubject: (state: any, subject: string) => (state.model.subject = subject)
}

const actions = {
  addCohort: ({commit, state}, cohort: any) => {
    const cohorts = state.addedCohorts.concat(cohort)
    $_recalculateStudentCount(state.sids, cohorts, state.addedCuratedGroups).then(sids => {
      commit('addCohort', cohort)
      commit('setCompleteSidSet', sids)
    }).finally(() => commit('setIsRecalculating', false))
  },
  addCuratedGroup: ({commit, state}, curatedGroup: any) => {
    const curatedGroups = state.addedCuratedGroups.concat(curatedGroup)
    $_recalculateStudentCount(state.sids, state.addedCohorts, curatedGroups).then(sids => {
      commit('addCuratedGroup', curatedGroup)
      commit('setCompleteSidSet', sids)
    }).finally(() => commit('setIsRecalculating', false))
  },
  addSid: $_addSid,
  addSidList: ({commit, state}, sidList: string[]) => {
    const sids = _.uniq(state.sids.concat(sidList))
    $_recalculateStudentCount(sids, state.addedCohorts, state.addedCuratedGroups).then(sids => {
      commit('addSidList', sidList)
      commit('setCompleteSidSet', sids)
    }).finally(() => commit('setIsRecalculating', false))
  },
  applyTemplate: ({commit, state}, template) => {
    applyNoteTemplate(state.model.id, template.id).then(note => commit('setModel', note))
  },
  clearAutoSaveJob: ({commit, state}) => {
    clearTimeout(state.autoSaveJob)
    commit('setAutoSaveJob', null)
  },
  exitSession: ({commit, state}, revert: boolean) => {
    return new Promise(resolve => {
      const mode = _.toString(state.mode)
      const done = note => {
        commit('exitSession')
        resolve(note)
      }
      if (revert) {
        if (state.model.id && ['createBatch', 'createNote'].includes(mode)) {
          deleteNote(state.model).then(() => done(null))
        } else if (mode === 'editNote' && state.model.isDraft) {
          commit('setModel', state.originalModel)
          $_updateAdvisingNote({commit, state}).then(done)
        } else {
          done(state.model)
        }
      } else {
        done(state.model)
      }
    })
  },
  async loadNoteTemplates({commit, state}) {
    if (_.isUndefined(state.myNoteTemplates)) {
      getMyNoteTemplates().then(templates => commit('setNoteTemplates', templates))
    }
  },
  removeAttachment: ({commit, state}, index: number) => {
    const attachmentId = state.model.attachments[index].id
    commit('removeAttachment', index)
    if (isAutoSaveMode(state.mode)) {
      removeAttachment(state.model.id, attachmentId).then(() => {
        alertScreenReader('Attachment removed', 'assertive')
      })
    }
  },
  removeCohort: ({commit, state}, cohort: any) => {
    const cohorts = _.reject(state.addedCohorts, ['id', cohort.id])
    $_recalculateStudentCount(state.sids, cohorts, state.addedCuratedGroups).then(sids => {
      commit('removeCohort', cohort)
      commit('setCompleteSidSet', sids)
    }).finally(() => commit('setIsRecalculating', false))
  },
  removeCuratedGroup: ({commit, state}, curatedGroup: any) => {
    const curatedGroups = _.reject(state.addedCuratedGroups, ['id', curatedGroup.id])
    $_recalculateStudentCount(state.sids, state.addedCohorts, curatedGroups).then(sids => {
      commit('removeCuratedGroup', curatedGroup)
      commit('setCompleteSidSet', sids)
    }).finally(() => commit('setIsRecalculating', false))
  },
  removeStudent: ({commit, state}, sid: string) => {
    const sids = _.without(state.sids, sid)
    $_recalculateStudentCount(sids, state.addedCohorts, state.addedCuratedGroups).then(sids => {
      commit('removeStudent', sid)
      commit('setCompleteSidSet', sids)
    }).finally(() => commit('setIsRecalculating', false))
  },
  resetModel: ({commit}, isPrivate?: any) => {
    const model = $_getDefaultModel()
    model.isPrivate = isPrivate
    commit('setModel', model)
  },
  setAutoSaveJob: ({commit, state}, jobId: number) => {
    clearTimeout(state.autoSaveJob)
    commit('setAutoSaveJob', jobId)
  },
  setIsRecalculating: ({commit}, isRecalculating: boolean) => commit('setIsRecalculating', isRecalculating),
  setModel: ({commit, state}, model?: any) => {
    commit('setModel', model)
    if (model.sid) {
      $_addSid({commit, state}, model.sid)
    }
  },
  updateAdvisingNote: $_updateAdvisingNote
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
