import _ from 'lodash'
import {getCuratedGroup} from '@/api/curated'
import store from '@/store'

export function goToCuratedGroup(curatedGroupId: number, pageNumber: number) {
  return new Promise(resolve => {
    store.commit('curatedGroup/setPageNumber', pageNumber)
    const user = store.getters['context/currentUser']
    const domain = store.getters['curatedGroup/domain']
    const itemsPerPage = store.getters['curatedGroup/itemsPerPage']
    const offset = _.multiply(pageNumber - 1, itemsPerPage)
    const orderBy = _.get(user.preferences, domain === 'admitted_students' ? 'admitSortBy' : 'sortBy')
    getCuratedGroup(
      curatedGroupId,
      itemsPerPage,
      offset,
      orderBy,
      user.preferences.termId
    ).then(group => {
      if (group) {
        store.commit('curatedGroup/setCuratedGroupName', group.name)
        store.commit('curatedGroup/setDomain', group.domain)
        store.commit('curatedGroup/setOwnerId', group.ownerId)
        store.commit('curatedGroup/setReferencingCohortIds', group.referencingCohortIds)
        store.commit('curatedGroup/setStudents', group.students)
        store.commit('curatedGroup/setTotalStudentCount', group.totalStudentCount)
        return resolve(group)
      } else {
        return resolve(null)
      }
    })
  })
}
