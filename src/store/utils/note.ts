import store from '@/store'
import {getDistinctSids} from '@/api/student'
import {map, trim} from 'lodash'
import {updateNote} from '@/api/notes'

export function addSid(sid: string) {
  const addedCohorts = store.getters['note/addedCohorts']
  const addedCuratedGroups = store.getters['note/addedCuratedGroups']
  const sids = store.getters['note/sids'].concat(sid)
  recalculateStudentCount(sids, addedCohorts, addedCuratedGroups).then(sids => {
    store.commit('note/addSid', sid)
    store.commit('note/setCompleteSidSet', sids)
  }).finally(() => store.commit('note/setIsRecalculating', false))
}

export function isAutoSaveMode(mode: string) {
  return ['createBatch', 'createNote', 'editDraft'].includes(mode)
}

export function recalculateStudentCount(sids: string[], cohorts: any[], curatedGroups: any[]) {
  return new Promise(resolve => {
    const cohortIds = map(cohorts, 'id')
    const curatedGroupIds = map(curatedGroups, 'id')
    if (cohortIds.length || curatedGroupIds.length) {
      getDistinctSids(sids, cohortIds, curatedGroupIds).then(data => resolve(data.sids))
    } else {
      resolve(sids)
    }
  })
}

export function updateAdvisingNote() {
  return new Promise(resolve => {
    const model = store.getters['note/model']
    const addedCohorts = store.getters['note/addedCohorts']
    const addedCuratedGroups = store.getters['note/addedCuratedGroups']
    const completeSidSet = store.getters['note/completeSidSet']

    store.commit('note/setBody', trim(model.body))
    const setDate = model.setDate ? model.setDate.format('YYYY-MM-DD') : null
    const sids: string[] = Array.from(completeSidSet)
    const isDraft = model.isDraft
    updateNote(
      model.id,
      model.body,
      map(addedCohorts, 'id'),
      model.contactType,
      map(addedCuratedGroups, 'id'),
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
