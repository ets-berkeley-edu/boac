import {get, isString, map, trim} from 'lodash'
import {deleteNote, removeAttachment, updateNote} from '@/api/notes'
import {getDistinctSids} from '@/api/student'
import {NoteEditSessionModel, NoteRecipients} from '@/stores/note-edit-session/index'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

export function exitSession(revert: boolean): Promise<NoteEditSessionModel | undefined> {
  return new Promise<NoteEditSessionModel | undefined>(resolve => {
    const mode: string | undefined = useNoteStore().mode
    const model: NoteEditSessionModel = useNoteStore().model
    const originalModel: NoteEditSessionModel = useNoteStore().originalModel
    const done = (note?: NoteEditSessionModel) => {
      useNoteStore().exitSession()
      resolve(note)
    }
    if (revert) {
      if (model.id && mode && ['createBatch', 'createNote'].includes(mode)) {
        deleteNote(model).then(() => done())
      } else if (mode === 'editNote' && model.isDraft) {
        useNoteStore().setModel(originalModel)
        updateAdvisingNote().then(done)
      } else {
        done(model)
      }
    } else {
      done(model)
    }
  })
}

export function isAutoSaveMode(mode: string | undefined): boolean {
  return mode ? ['createBatch', 'createNote', 'editDraft'].includes(mode) : false
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
  const autoSaveDraftNote = () => {
    const model: NoteEditSessionModel = useNoteStore().model
    useNoteStore().clearAutoSaveJob()
    if (model.isDraft) {
      useNoteStore().setIsAutoSavingDraftNote(true)
      updateAdvisingNote().then((note: any) => {
        useNoteStore().setModelId(note.id)
        setTimeout(() => useNoteStore().setIsAutoSavingDraftNote(false), 2000)
        scheduleAutoSaveJob()
      })
    }
  }
  const interval = get(useContextStore().config, 'notesDraftAutoSaveInterval')
  const jobId = setTimeout(autoSaveDraftNote, interval)
  useNoteStore().setAutoSaveJob(jobId)
}

export function setNoteRecipient(sid): Promise<void> {
  const recipients: NoteRecipients = useNoteStore().recipients
  return setNoteRecipients(
    recipients.cohorts,
    recipients.curatedGroups,
    recipients.sids.concat(sid)
  )
}

export function setNoteRecipients(cohorts, curatedGroups, sids): Promise<void> {
  return new Promise(resolve => {
    useNoteStore().setIsRecalculating(true)
    useNoteStore().setRecipients({cohorts, curatedGroups, sids})
    const cohortIds = map(cohorts, 'id')
    const curatedGroupIds = map(curatedGroups, 'id')
    const onFinish = sids => {
      useNoteStore().setCompleteSidSet(sids)
      useNoteStore().setIsRecalculating(false)
      resolve()
    }
    const recipients: NoteRecipients = useNoteStore().recipients
    if (cohortIds.length || curatedGroupIds.length) {
      getDistinctSids(recipients.sids, cohortIds, curatedGroupIds).then(data => onFinish(data.sids))
    } else {
      onFinish(recipients.sids)
    }
  })
}

export function setSubjectPerEvent(event: any): void {
  useNoteStore().setSubject(isString(event) ? event : event.target.value)
}

export function updateAdvisingNote(): Promise<any> {
  return new Promise<any>(resolve => {
    const completeSidSet: Set<string> = useNoteStore().completeSidSet
    const model: NoteEditSessionModel = useNoteStore().model
    const recipients: NoteRecipients = useNoteStore().recipients

    useNoteStore().setBody(trim(model.body))
    const setDate = model.setDate ? model.setDate.format('YYYY-MM-DD') : null
    const sids: string[] = Array.from(completeSidSet)
    const isDraft = model.isDraft
    updateNote(
      model.id,
      model.body,
      map(recipients.cohorts, 'id'),
      model.contactType,
      map(recipients.curatedGroups, 'id'),
      isDraft,
      model.isPrivate,
      setDate,
      sids,
      model.subject,
      [],
      model.topics
    ).then(resolve)
  })
}

export function removeAttachmentByIndex(index: number) {
  const mode: string | undefined = useNoteStore().mode
  const model: NoteEditSessionModel = useNoteStore().model
  if (model.attachments && index < model.attachments.length) {
    const attachmentId: number = model.attachments[index].id
    useNoteStore().removeAttachmentByIndex(index)
    if (isAutoSaveMode(mode)) {
      removeAttachment(model.id, attachmentId).then(() => {
        useContextStore().alertScreenReader('Attachment removed', 'assertive')
      })
    }
  }
}
