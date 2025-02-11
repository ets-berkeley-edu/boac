import {Attachment, NoteEditSessionModel, NoteRecipients, NoteTemplate} from '@/lib/types'
import {cloneDeep, find, isNil, noop, sortBy} from 'lodash'
import {StoreDefinition, defineStore} from 'pinia'
import {onVisibilityChange} from '@/stores/note-edit-session/utils'

const VALID_MODES = ['createBatch', 'createNote', 'editDraft', 'editNote', 'editTemplate']

function $_getDefaultModel(): NoteEditSessionModel {
  return {
    id: NaN,
    attachments: [] as Attachment[],
    author: {},
    body: undefined,
    contactType: undefined,
    deleteAttachmentIds: [],
    isDraft: false,
    isPrivate: false,
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

export const useNoteStore: StoreDefinition = defineStore('note', {
  state: () => ({
    autoSaveJob: undefined as number | null | undefined,
    boaSessionExpired: false,
    completeSidSet: new Set<string>(),
    isAutoSavingDraftNote: false,
    isCreateNoteModalOpen: false,
    isFocusLockDisabled: false,
    isSaving: false,
    isRecalculating: false,
    mode: undefined as string | undefined,
    model: $_getDefaultModel(),
    noteTemplates: new Array<NoteTemplate>(),
    originalModel: $_getDefaultModel(),
    recipients: $_getDefaultRecipients(),
    template: undefined
  }),
  getters: {
    disableNewNoteButton: state => !!state.mode
  },
  actions: {
    addTopic(topic: string) {
      this.model.topics.push(topic)
    },
    clearAutoSaveJob() {
      if (this.autoSaveJob !== null) {
        clearTimeout(this.autoSaveJob)
        this.autoSaveJob = null
      }
    },
    exitSession() {
      document.onvisibilitychange = noop
      if (this.autoSaveJob !== null) {
        clearTimeout(this.autoSaveJob)
        this.autoSaveJob = null
      }
      this.recipients = $_getDefaultRecipients()
      this.completeSidSet = new Set()
      this.isSaving = false
      this.mode = undefined
      this.model = $_getDefaultModel()
      this.originalModel = cloneDeep(this.model)
      this.recipients.sids = []
    },
    onBoaSessionExpires() {
      this.boaSessionExpired = true
    },
    onUpdateTemplate(template: NoteTemplate) {
      const indexOf = this.noteTemplates.findIndex(t => t.id === template.id)
      Object.assign(this.noteTemplates[indexOf], template)
    },
    removeAllStudents() {
      this.recipients.sids = []
    },
    removeAttachmentByIndex(index: number) {
      const attachment = this.model.attachments[index]
      if (attachment.id) {
        this.model.deleteAttachmentIds.push(attachment.id)
      }
      this.model.attachments.splice(index, 1)
    },
    removeTopic(topic: string) {
      this.model.topics.splice(this.model.topics.indexOf(topic), 1)
    },
    resetModel() {
      this.model = $_getDefaultModel()
    },
    setAttachments(attachments: Attachment[]) {
      this.model.attachments = sortBy(attachments, ['name', 'id'])
    },
    setAutoSaveJob(jobId: number | null) {
      if (this.autoSaveJob !== null) {
        clearTimeout(this.autoSaveJob)
      }
      this.autoSaveJob = jobId
      if (jobId) {
        document.onvisibilitychange = onVisibilityChange
      }
    },
    setBody(body: string) {
      this.model.body = body
    },
    setCompleteSidSet(completeSidSet: string[]) {
      this.completeSidSet = new Set(completeSidSet)
    },
    setContactType(contactType: string) {
      this.model.contactType = contactType
    },
    setFocusLockDisabled(isDisabled: boolean) {
      this.isFocusLockDisabled = isDisabled
    },
    setIsAutoSavingDraftNote(value: boolean) {
      this.isAutoSavingDraftNote = value
    },
    setIsCreateNoteModalOpen(value: boolean) {
      this.isCreateNoteModalOpen = value
    },
    setIsDraft(isDraft: boolean) {
      this.model.isDraft = isDraft
    },
    setIsPrivate(isPrivate: boolean) {
      this.model.isPrivate = isPrivate
    },
    setIsRecalculating(isRecalculating: boolean) {
      this.isRecalculating = isRecalculating
    },
    setIsSaving(isSaving: boolean) {
      this.isSaving = isSaving
    },
    setMode(mode: string) {
      if (isNil(mode)) {
        this.mode = undefined
      } else if (find(VALID_MODES, type => mode.match(type))) {
        this.mode = mode
      } else {
        throw new TypeError('Invalid mode: ' + mode)
      }
    },
    setModelId(modelId: number) {
      this.model.id = modelId
    },
    setModel(note?: NoteEditSessionModel) {
      if (note) {
        const model = cloneDeep(note)
        this.model = {
          attachments: model.attachments || [],
          author: model.author || {},
          body: model.body,
          contactType: model.contactType || null,
          deleteAttachmentIds: [],
          id: model.id,
          isDraft: model.isDraft,
          isPrivate: model.isPrivate,
          setDate: model.setDate,
          subject: model.subject,
          topics: model.topics || [],
        }
      } else {
        this.model = $_getDefaultModel()
      }
      this.originalModel = cloneDeep(this.model)
    },
    setNoteTemplates(templates: NoteTemplate[]) {
      this.noteTemplates = templates
    },
    setRecipients(recipients: NoteRecipients) {
      this.recipients = recipients
    },
    setSetDate(setDate: string) {
      this.model.setDate = setDate
    },
    setSubject(subject: string) {
      this.model.subject = subject
    }
  }
})
