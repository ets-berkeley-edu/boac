import _ from 'lodash'
import moment, {Moment} from 'moment'
import store from '@/store'
import {addAttachments, applyNoteTemplate, deleteNote, removeAttachment, updateNote} from '@/api/notes'
import {getMyNoteTemplates} from '@/api/note-templates'
import {isAutoSaveMode} from '@/store/modules/note-edit-session/utils'

const VALID_MODES = ['createBatch', 'createNote', 'editDraft', 'editNote', 'editTemplate']

type NoteEditSessionModel = {
  id: number;
  attachments?: string[];
  body?: string;
  contactType?: string;
  deleteAttachmentIds?: number[];
  isDraft?: boolean;
  isPrivate?: boolean;
  setDate?: any;
  subject?: string;
  topics?: string[];
}

type NoteRecipients = {
  cohorts: any[],
  curatedGroups: any[],
  sids: string[]
}

function $_getDefaultModel(): NoteEditSessionModel {
  return {
    id: NaN,
    attachments: [],
    body: undefined,
    contactType: undefined,
    deleteAttachmentIds: [],
    isDraft: undefined,
    isPrivate: undefined,
    setDate: undefined,
    subject: undefined,
    topics: []
  }
}

function $_getDefaultRecipients(): NoteRecipients {
  return {
    cohorts: [],
    curatedGroups: [],
    sids: []
  }
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
      _.map(state.recipients.cohorts, 'id'),
      state.model.contactType,
      _.map(state.recipients.curatedGroups, 'id'),
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
  recipients: $_getDefaultRecipients()
}

const getters = {
  autoSaveJob: (state: any): any => state.autoSaveJob,
  boaSessionExpired: (state: any): any[] => state.boaSessionExpired,
  completeSidSet: (state: any): number[] => Array.from(state.completeSidSet),
  disableNewNoteButton: (state: any): boolean => !!state.mode,
  isAutoSavingDraftNote: (state: any): boolean => state.isAutoSavingDraftNote,
  isFocusLockDisabled: (state: any): boolean => state.isFocusLockDisabled,
  isSaving: (state: any): boolean => state.isSaving,
  isRecalculating: (state: any): boolean => state.isRecalculating,
  mode: (state: any): string => state.mode,
  model: (state: any): any => state.model,
  noteTemplates: (state: any): any[] => state.noteTemplates,
  recipients: (state: any): NoteRecipients => state.recipients,
  template: (state: any): any => state.template
}

const mutations = {
  addAttachments: (state: any, attachments: any[]) => {
    state.model.attachments = _.sortBy(attachments, ['name', 'id'])
  },
  addTopic: (state: any, topic: string) => (state.model.topics.push(topic)),
  exitSession: (state: any) => {
    clearTimeout(state.autoSaveJob)
    state.autoSaveJob = null
    state.recipients = $_getDefaultRecipients()
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
  removeAllStudents: (state: any) => state.recipients.sids = [],
  removeAttachment: (state: any, index: number) => {
    const attachment = state.model.attachments[index]
    if (attachment.id) {
      state.model.deleteAttachmentIds.push(attachment.id)
    }
    state.model.attachments.splice(index, 1)
  },
  removeTopic: (state: any, topic: string) => (state.model.topics.splice(state.model.topics.indexOf(topic), 1)),
  resetModel: (state: any) => state.model = $_getDefaultModel(),
  setAutoSaveJob: (state: any, jobId: number) => state.autoSaveJob = jobId,
  setBody: (state: any, body: string) => (state.model.body = body),
  setCompleteSidSet: (state: any, completeSidSet: number[]) => state.completeSidSet = new Set(completeSidSet),
  setContactType: (state: any, contactType: string) => (state.model.contactType = contactType),
  setFocusLockDisabled: (state: any, isDisabled: boolean) => (state.isFocusLockDisabled = isDisabled),
  setIsDraft: (state: any, isDraft: boolean) => (state.model.isDraft = isDraft),
  setIsPrivate: (state: any, isPrivate: boolean) => (state.model.isPrivate = isPrivate),
  setIsRecalculating: (state: any, isRecalculating: boolean) => (state.isRecalculating = isRecalculating),
  setIsSaving: (state: any, isSaving: boolean) => (state.isSaving = isSaving),
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
  setRecipients: (state: any, recipients: NoteRecipients) => state.recipients = recipients,
  setSetDate: (state: any, setDate: any): Moment | null => state.model.setDate = setDate ? moment(setDate) : null,
  setSubject: (state: any, subject: string) => (state.model.subject = subject)
}

const actions = {
  addAttachments: ({commit, state}, attachments: any[]) => {
    if (isAutoSaveMode(state.mode)) {
      commit('setIsSaving', true)
      addAttachments(state.model.id, attachments).then(response => {
        commit('addAttachments', response.attachments)
        store.commit('context/alertScreenReader', {message: 'Attachment added', politeness: 'assertive'})
        commit('setIsSaving', false)
      })
    } else {
      commit('addAttachments', attachments)
    }
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
        store.commit('context/alertScreenReader', {
          message: 'Attachment removed',
          politeness: 'assertive'
        })
      })
    }
  },
  setAutoSaveJob: ({commit, state}, jobId: number) => {
    clearTimeout(state.autoSaveJob)
    commit('setAutoSaveJob', jobId)
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
