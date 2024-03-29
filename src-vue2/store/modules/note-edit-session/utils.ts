import {isString, map, trim} from 'lodash'
import store from '@/store'
import {alertScreenReader} from '@/store/modules/context'
import {deleteNote, removeAttachment, updateNote} from '@/api/notes'
import {getDistinctSids} from '@/api/student'
import {NoteEditSessionModel, NoteRecipients} from '@/store/modules/note-edit-session/index'

export function clearAutoSaveJob(): void {
  const jobId: number = store.getters['note/autoSaveJob']
  clearTimeout(jobId)
  store.commit('note/setAutoSaveJob', null)
}

export function exitSession(revert: boolean): Promise<NoteEditSessionModel | undefined> {
  return new Promise<NoteEditSessionModel | undefined>(resolve => {
    const mode: string = store.getters['note/mode']
    const model: NoteEditSessionModel = store.getters['note/model']
    const originalModel: NoteEditSessionModel = store.getters['note/originalModel']
    const done = (note?: NoteEditSessionModel) => {
      store.commit('note/exitSession')
      resolve(note)
    }
    if (revert) {
      if (model.id && ['createBatch', 'createNote'].includes(mode)) {
        deleteNote(model).then(() => done())
      } else if (mode === 'editNote' && model.isDraft) {
        store.commit('note/setModel', originalModel)
        updateAdvisingNote().then(done)
      } else {
        done(model)
      }
    } else {
      done(model)
    }
  })
}

export function isAutoSaveMode(mode: string): boolean {
  return ['createBatch', 'createNote', 'editDraft'].includes(mode)
}

export function onVisibilityChange(): void {
  const visibility: 'hidden' | 'visible' = document.visibilityState
  if (visibility) {
    clearAutoSaveJob()
    if (visibility === 'visible') {
      scheduleAutoSaveJob()
    }
  }
}

export function scheduleAutoSaveJob() {
  const autoSaveDraftNote = () => {
    const model: NoteEditSessionModel = store.getters['note/model']
    clearAutoSaveJob()
    if (model.isDraft) {
      store.commit('note/isAutoSavingDraftNote', true)
      updateAdvisingNote().then((note: any) => {
        store.commit('note/setModelId', note.id)
        setTimeout(() => store.commit('note/isAutoSavingDraftNote', false), 2000)
        scheduleAutoSaveJob()
      })
    }
  }
  const interval = store.getters['context/config'].notesDraftAutoSaveInterval
  const jobId = setTimeout(autoSaveDraftNote, interval)
  store.commit('note/setAutoSaveJob', jobId)
}

export function setNoteRecipient(sid): Promise<void> {
  const recipients: NoteRecipients = store.getters['note/recipients']
  return setNoteRecipients(
    recipients.cohorts,
    recipients.curatedGroups,
    recipients.sids.concat(sid)
  )
}

export function setNoteRecipients(cohorts, curatedGroups, sids): Promise<void> {
  return new Promise(resolve => {
    store.commit('note/setIsRecalculating', true)
    store.commit('note/setRecipients', {cohorts, curatedGroups, sids})
    const cohortIds = map(cohorts, 'id')
    const curatedGroupIds = map(curatedGroups, 'id')
    const onFinish = sids => {
      store.commit('note/setCompleteSidSet', sids)
      store.commit('note/setIsRecalculating', false)
      resolve()
    }
    const recipients: NoteRecipients = store.getters['note/recipients']
    if (cohortIds.length || curatedGroupIds.length) {
      getDistinctSids(recipients.sids, cohortIds, curatedGroupIds).then(data => onFinish(data.sids))
    } else {
      onFinish(recipients.sids)
    }
  })
}

export function setSubjectPerEvent(event: any): void {
  store.commit('note/setSubject', isString(event) ? event : event.target.value)
}

export function updateAdvisingNote(): Promise<any> {
  return new Promise<any>(resolve => {
    const completeSidSet: string[] = store.getters['note/completeSidSet']
    const model: NoteEditSessionModel = store.getters['note/model']
    const recipients: NoteRecipients = store.getters['note/recipients']

    store.commit('note/setBody', trim(model.body))
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
  const mode: string = store.getters['note/mode']
  const model: NoteEditSessionModel = store.getters['note/model']
  if (model.attachments && index < model.attachments.length) {
    const attachmentId: number = model.attachments[index].id
    store.commit('note/removeAttachmentByIndex', index)
    if (isAutoSaveMode(mode)) {
      removeAttachment(model.id, attachmentId).then(() => {
        alertScreenReader('Attachment removed', 'assertive')
      })
    }
  }
}
