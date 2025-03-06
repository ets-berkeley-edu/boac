import {get, isNil, isString, map, trim} from 'lodash'
import type {Attachment, Cohort, CuratedGroup, NoteEditSessionModel, NoteRecipients} from '@/lib/types'
import {deleteNote, updateNote} from '@/api/notes'
import {getDistinctSids} from '@/api/student'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'
import {createPeerAdvisingNote, updatePeerAdvisingNote} from '@/api/peer-advising-notes'

export function clearNoteRecipients(): Promise<void> {
  return setNoteRecipients([], [], [])
}

export function disableFocusLock(): void {
  useNoteStore().setFocusLockDisabled(true)
}

export function enableFocusLock(): void {
  setTimeout(() => useNoteStore().setFocusLockDisabled(false), 500)
}

export function exitSession(revert: boolean): Promise<NoteEditSessionModel | void> {
  return new Promise<NoteEditSessionModel | void>(resolve => {
    const noteStore = useNoteStore()
    const mode: string | undefined = noteStore.mode
    const model: NoteEditSessionModel = noteStore.model
    const originalModel: NoteEditSessionModel = noteStore.originalModel
    const done = (note?: NoteEditSessionModel | void) => {
      noteStore.exitSession()
      resolve(note)
    }
    if (revert) {
      if (model.id && mode && ['createBatch', 'createNote'].includes(mode)) {
        deleteNote(model).then(done)
      } else if (mode === 'editNote' && model.isDraft) {
        noteStore.setModel(originalModel)
        updateAdvisingNote().then(done)
      } else {
        done(model)
      }
    } else {
      done(model)
    }
  })
}

export function getDefaultModel(): NoteEditSessionModel {
  return {
    id: NaN,
    attachments: [] as Attachment[],
    author: {},
    body: undefined,
    contactType: undefined,
    deleteAttachmentIds: [],
    isDraft: false,
    isPrivate: false,
    peerAdvisingDepartmentId: undefined,
    setDate: undefined,
    subject: undefined,
    topics: []
  }
}

export function isAutoSaveMode(mode: string | undefined): boolean {
  return mode ? ['createBatch', 'createNote', 'editDraft', 'editNote'].includes(mode) : false
}

export function onVisibilityChange(): void {
  const visibility: 'hidden' | 'visible' = document.visibilityState
  if (visibility) {
    useNoteStore().clearAutoSaveJob()
    if (visibility === 'visible') {
      scheduleAutoSaveJob()
    }
  }
}

export function scheduleAutoSaveJob() {
  const noteStore = useNoteStore()
  const autoSaveDraftNote = () => {
    const model: NoteEditSessionModel = noteStore.model
    noteStore.clearAutoSaveJob()
    if (model.isDraft) {
      noteStore.setIsAutoSavingDraftNote(true)
      updateAdvisingNote().then((note: NoteEditSessionModel) => {
        noteStore.setModelId(note.id)
        setTimeout(() => noteStore.setIsAutoSavingDraftNote(false), 2000)
        scheduleAutoSaveJob()
      })
    }
  }
  const interval = useContextStore().config.notesDraftAutoSaveInterval
  const jobId = setTimeout(autoSaveDraftNote, interval)
  noteStore.setAutoSaveJob(jobId)
}

export function setNoteRecipient(sid: string): Promise<void> {
  const recipients: NoteRecipients = useNoteStore().recipients
  return setNoteRecipients(
    recipients.cohorts || [],
    recipients.curatedGroups || [],
    recipients.sids.concat(sid)
  )
}

export function setNoteRecipients(cohorts: Cohort[], curatedGroups: CuratedGroup[], sids: string[]): Promise<void> {
  return new Promise(resolve => {
    const noteStore = useNoteStore()
    noteStore.setIsRecalculating(true)
    noteStore.setRecipients({cohorts, curatedGroups, sids})
    const cohortIds = map(cohorts, 'id')
    const curatedGroupIds = map(curatedGroups, 'id')
    const onFinish = (sids: string[]) => {
      noteStore.setCompleteSidSet(sids)
      noteStore.setIsRecalculating(false)
      resolve()
    }
    const recipients: NoteRecipients = noteStore.recipients
    if (cohortIds.length || curatedGroupIds.length) {
      getDistinctSids(recipients.sids, cohortIds, curatedGroupIds).then(data => onFinish(data.sids))
    } else {
      onFinish(recipients.sids)
    }
  })
}

export function setSubjectPerEvent(event: Event): void {
  useNoteStore().setSubject(isString(event) ? event : get(event.target, 'value'))
}

export function updateAdvisingNote(): Promise<NoteEditSessionModel> {
  return new Promise<NoteEditSessionModel>(resolve => {
    const noteStore = useNoteStore()
    const completeSidSet: Set<string> = noteStore.completeSidSet
    const model: NoteEditSessionModel = noteStore.model
    const recipients: NoteRecipients = noteStore.recipients

    noteStore.setBody(trim(model.body))
    const sids: string[] = Array.from(completeSidSet)
    const isDraft = model.isDraft
    if (noteStore.mode === 'createPeerAdvisorNote') {
      if (model.body && model.peerAdvisingDepartmentId && !isNil(model.subject)) {
        createPeerAdvisingNote(
          model.body,
          model.contactType,
          model.peerAdvisingDepartmentId,
          sids[0],
          model.subject,
          model.topics
        ).then(note => {
          noteStore.setModel(note)
          resolve(note)
        })
      } else {
        throw new Error('Peer Advising notes require fields which are optional for standard notes.')
      }
    } else {
      if (model.peerAdvisingDepartmentId) {
        updatePeerAdvisingNote(
          model.id,
          model.body,
          model.contactType,
          model.subject,
          model.topics
        ).then(resolve)
      } else {
        updateNote(
          model.id,
          model.body,
          map(recipients.cohorts, 'id'),
          model.contactType,
          map(recipients.curatedGroups, 'id'),
          isDraft,
          model.isPrivate,
          model.setDate,
          sids,
          model.subject,
          [],
          model.topics
        ).then(resolve)
      }
    }
  })
}
