import _ from 'lodash'
import {getCuratedGroup} from '@/api/curated'
import {useContextStore} from '@/stores/context'
import {useCuratedGroupStore} from '@stores/curated-group/index'

export function goToCuratedGroup(curatedGroupId: number, pageNumber: number) {
  return new Promise(resolve => {
    useCuratedGroupStore().setPageNumber(pageNumber)
    const user = useContextStore().currentUser
    const domain = useCuratedGroupStore().domain
    const itemsPerPage = useCuratedGroupStore().itemsPerPage
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
        useCuratedGroupStore().setCuratedGroupName(group.name)
        useCuratedGroupStore().setDomain(group.domain)
        useCuratedGroupStore().setOwnerId(group.ownerId)
        useCuratedGroupStore().setReferencingCohortIds(group.referencingCohortIds)
        useCuratedGroupStore().setStudents(group.students)
        useCuratedGroupStore().setTotalStudentCount(group.totalStudentCount)
      }
      resolve(group)
    })
  })
}
