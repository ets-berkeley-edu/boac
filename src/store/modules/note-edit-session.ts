import _ from 'lodash'
import Vue from 'vue'
import {createNotes} from '@/api/notes'
import {getDistinctSids} from '@/api/student'
import {getMyNoteTemplates} from '@/api/note-templates'

const VALID_MODES = ['batch', 'create', 'edit', 'editTemplate']

const $_getDefaultModel = (isPrivate?) => {
  return {
    id: undefined,
    subject: undefined,
    body: undefined,
    contactType: undefined,
    isPrivate: _.isNil(isPrivate) ? undefined : isPrivate,
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
const state = {
  addedCohorts: [],
  addedCuratedGroups: [],
  boaSessionExpired: false,
  completeSidSet: [],
  isFocusLockDisabled: undefined,
  isSaving: false,
  isRecalculating: false,
  mode: undefined,
  model: $_getDefaultModel(),
  noteTemplates: undefined,
  sids: []
}

const getters = {
  addedCohorts: (state: any): any[] => state.addedCohorts,
  addedCuratedGroups: (state: any): any[] => state.addedCuratedGroups,
  boaSessionExpired: (state: any): any[] => state.boaSessionExpired,
  disableNewNoteButton: (state: any): boolean => !!state.mode,
  isFocusLockDisabled: (state: any): boolean => state.isFocusLockDisabled,
  isSaving: (state: any): boolean => state.isSaving,
  isRecalculating: (state: any): boolean => state.isRecalculating,
  mode: (state: any): string => state.mode,
  model: (state: any): any => state.model,
  noteTemplates: (state: any): any[] => state.noteTemplates,
  sids: (state: any): string[] => state.sids,
  completeSidSet: (state: any): number => state.completeSidSet,
  template: (state: any): any => state.template
}

const mutations = {
  addAttachment: (state: any, attachment: any) => (state.model.attachments.push(attachment)),
  addCohort: (state: any, cohort: any) => state.addedCohorts.push(cohort),
  addCuratedGroup: (state: any, curatedGroup: any) => state.addedCuratedGroups.push(curatedGroup),
  addSid: (state: any, sid: string) => state.sids.push(sid),
  addTopic: (state: any, topic: string) => (state.model.topics.push(topic)),
  onBoaSessionExpires: (state: any) => (state.boaSessionExpired = true),
  exitSession: (state: any) => {
    state.addedCohorts = []
    state.addedCuratedGroups = []
    state.completeSidSet = []
    state.isSaving = false
    state.mode = undefined
    state.model = $_getDefaultModel()
    state.sids = []
  },
  onCreateTemplate: (state: any, template) => state.noteTemplates = _.orderBy(state.noteTemplates.concat([template]), ['title'], ['asc']),
  onDeleteTemplate: (state: any, templateId: any) => {
    const indexOf = state.noteTemplates.findIndex(template => template.id === templateId)
    state.noteTemplates.splice(indexOf, 1)
  },
  onUpdateTemplate: (state: any, template: any) => {
    const indexOf = state.noteTemplates.findIndex(t => t.id === template.id)
    Object.assign(state.noteTemplates[indexOf], template)
  },
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
  setBody: (state: any, body: string) => (state.model.body = body),
  setCompleteSidSet: (state: any, completeSidSet: number) => (state.completeSidSet = completeSidSet),
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
  setModel: (state: any, model: any) => {
    if (model) {
      state.model = {
        attachments: model.attachments || [],
        body: model.body,
        contactType: model.contactType || null,
        deleteAttachmentIds: [],
        id: model.id,
        isPrivate: model.isPrivate,
        setDate: model.setDate ? Vue.prototype.$moment(model.setDate) : null,
        subject: model.subject,
        topics: model.topics || [],
      }
    } else {
      state.model = $_getDefaultModel()
    }
  },
  setNoteTemplates: (state: any, templates: any[]) => state.noteTemplates = templates,
  setIsPrivate: (state: any, isPrivate: boolean) => (state.model.isPrivate = isPrivate),
  setSetDate: (state: any, setDate: any) => (state.model.setDate = setDate ? Vue.prototype.$moment(setDate) : null),
  setSubject: (state: any, subject: string) => (state.model.subject = subject)
}

const actions = {
  addAttachment: ({commit}, attachment: any) => commit('addAttachment', attachment),
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
  addSid: ({commit, state}, sid: string) => {
    const sids = state.sids.concat(sid)
    $_recalculateStudentCount(sids, state.addedCohorts, state.addedCuratedGroups).then(sids => {
      commit('addSid', sid)
      commit('setCompleteSidSet', sids)
    }).finally(() => commit('setIsRecalculating', false))
  },
  addTopic: ({commit}, topic: string) => commit('addTopic', topic),
  onBoaSessionExpires: ({commit}) => commit('onBoaSessionExpires'),
  createAdvisingNotes: ({commit, state}) => {
    return new Promise(resolve => {
      commit('setBody', _.trim(state.model.body))
      const [templateAttachments, attachments] = state.model.attachments.reduce((result, a) => {
        result[a.noteTemplateId ? 0 : 1].push(a)
        return result
      }, [[], []])
      Vue.prototype.$eventHub.emit('begin-note-creation', {
        completeSidSet: state.completeSidSet,
        subject: state.model.subject
      })
      const dateString = state.model.setDate ? state.model.setDate.format('YYYY-MM-DD') : null
      createNotes(
        attachments,
        state.model.body,
        _.map(state.addedCohorts, 'id'),
        state.model.contactType,
        _.map(state.addedCuratedGroups, 'id'),
        state.model.isPrivate,
        dateString,
        state.sids,
        state.model.subject,
        _.map(templateAttachments, 'id'),
        state.model.topics
      ).then(data => {
        const eventType = state.completeSidSet.length > 1 ? 'batch-of-notes-created' : 'advising-note-created'
        Vue.prototype.$eventHub.emit(eventType, data)
        resolve(data)
      })
    })
  },
  exitSession: ({commit}) => commit('exitSession'),
  async loadNoteTemplates({commit, state}) {
    if (_.isUndefined(state.myNoteTemplates)) {
      getMyNoteTemplates().then(templates => commit('setNoteTemplates', templates))
    }
  },
  onCreateTemplate: ({commit}, template: any) => commit('onCreateTemplate', template),
  onDeleteTemplate: ({commit}, templateId: number) => commit('onDeleteTemplate', templateId),
  onUpdateTemplate: ({commit}, template: any) => commit('onUpdateTemplate', template),
  removeAttachment: ({commit}, index: number) => commit('removeAttachment', index),
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
  removeTopic: ({commit}, topic: string) => commit('removeTopic', topic),
  resetModel: ({commit}, isPrivate?: boolean) => commit('setModel', $_getDefaultModel(isPrivate)),
  setBody: ({commit}, body: string) => commit('setBody', body),
  setContactType: ({commit}, contactType: string) => commit('setContactType', contactType),
  setFocusLockDisabled: ({commit}, isDisabled: boolean) => commit('setFocusLockDisabled', isDisabled),
  setIsPrivate: ({commit}, isPrivate: boolean) => commit('setIsPrivate', isPrivate),
  setIsRecalculating: ({commit}, isRecalculating: boolean) => commit('setIsRecalculating', isRecalculating),
  setIsSaving: ({commit}, isSaving: boolean) => commit('setIsSaving', isSaving),
  setMode: ({commit}, mode: string) => commit('setMode', mode),
  setModel: ({commit}, model?: any) => commit('setModel', model),
  setSetDate: ({commit}, setDate: any) => commit('setSetDate', setDate),
  setSubject: ({commit}, subject: string) => commit('setSubject', subject)
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
