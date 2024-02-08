import moment, {Moment} from 'moment'
import {cloneDeep, find, isNil, sortBy} from 'lodash'

const VALID_MODES = ['createBatch', 'createNote', 'editDraft', 'editNote', 'editTemplate']

export type NoteEditSessionModel = {
  id: number;
  attachments?: any[];
  body?: string;
  contactType?: string;
  deleteAttachmentIds?: number[];
  isDraft?: boolean;
  isPrivate?: boolean;
  setDate?: any;
  subject?: string;
  topics?: string[];
}

export type NoteRecipients = {
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
  autoSaveJob: (state: any): number => state.autoSaveJob,
  boaSessionExpired: (state: any): any[] => state.boaSessionExpired,
  completeSidSet: (state: any): string[] => Array.from(state.completeSidSet),
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
  addTopic: (state: any, topic: string) => (state.model.topics.push(topic)),
  exitSession: (state: any) => {
    clearTimeout(state.autoSaveJob)
    state.autoSaveJob = null
    state.recipients = $_getDefaultRecipients()
    state.completeSidSet = new Set()
    state.isSaving = false
    state.mode = undefined
    state.model = $_getDefaultModel()
    state.originalModel = cloneDeep(state.model)
    state.sids = []
  },
  isAutoSavingDraftNote: (state: any, value: boolean) => state.isAutoSavingDraftNote = value,
  onBoaSessionExpires: (state: any) => state.boaSessionExpired = true,
  onUpdateTemplate: (state: any, template: any) => {
    const indexOf = state.noteTemplates.findIndex(t => t.id === template.id)
    Object.assign(state.noteTemplates[indexOf], template)
  },
  removeAllStudents: (state: any) => state.recipients.sids = [],
  removeAttachmentByIndex: (state: any, index: number) => {
    const attachment = state.model.attachments[index]
    if (attachment.id) {
      state.model.deleteAttachmentIds.push(attachment.id)
    }
    state.model.attachments.splice(index, 1)
  },
  removeTopic: (state: any, topic: string) => (state.model.topics.splice(state.model.topics.indexOf(topic), 1)),
  resetModel: (state: any) => state.model = $_getDefaultModel(),
  setAttachments: (state: any, attachments: any[]) => state.model.attachments = sortBy(attachments, ['name', 'id']),
  setAutoSaveJob: (state: any, jobId: number) => {
    clearTimeout(state.autoSaveJob)
    state.autoSaveJob = jobId
  },
  setBody: (state: any, body: string) => (state.model.body = body),
  setCompleteSidSet: (state: any, completeSidSet: number[]) => state.completeSidSet = new Set(completeSidSet),
  setContactType: (state: any, contactType: string) => (state.model.contactType = contactType),
  setFocusLockDisabled: (state: any, isDisabled: boolean) => (state.isFocusLockDisabled = isDisabled),
  setIsDraft: (state: any, isDraft: boolean) => (state.model.isDraft = isDraft),
  setIsPrivate: (state: any, isPrivate: boolean) => (state.model.isPrivate = isPrivate),
  setIsRecalculating: (state: any, isRecalculating: boolean) => (state.isRecalculating = isRecalculating),
  setIsSaving: (state: any, isSaving: boolean) => (state.isSaving = isSaving),
  setMode: (state: any, mode: string) => {
    if (isNil(mode)) {
      state.mode = undefined
    } else if (find(VALID_MODES, type => mode.match(type))) {
      state.mode = mode
    } else {
      throw new TypeError('Invalid mode: ' + mode)
    }
  },
  setModelId: (state: any, modelId: number) => state.model.id = modelId,
  setModel: (state: any, note?: any) => {
    if (note) {
      const model = cloneDeep(note)
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
    state.originalModel = cloneDeep(state.model)
  },
  setNoteTemplates: (state: any, templates: any[]) => state.noteTemplates = templates,
  setRecipients: (state: any, recipients: NoteRecipients) => state.recipients = recipients,
  setSetDate: (state: any, setDate: any): Moment | null => state.model.setDate = setDate ? moment(setDate) : null,
  setSubject: (state: any, subject: string) => (state.model.subject = subject)
}

export default {
  getters,
  mutations,
  namespaced: true,
  state
}
