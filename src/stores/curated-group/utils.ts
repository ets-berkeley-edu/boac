import {get, multiply} from 'lodash'
import {getCuratedGroup} from '@/api/curated'
import {useContextStore} from '@/stores/context'
import {useCuratedGroupStore} from '@/stores/curated-group/index'
import {BoaUser} from '@/lib/types'

export function goToCuratedGroup(curatedGroupId: number, pageNumber: number) {
  return new Promise(resolve => {
    const groupStore = useCuratedGroupStore()
    const currentUser: BoaUser = useContextStore().currentUser
    const domain = groupStore.domain
    const itemsPerPage = groupStore.itemsPerPage
    const offset: number = multiply(pageNumber - 1, itemsPerPage)
    const orderBy: string = get(currentUser.preferences, domain === 'admitted_students' ? 'admitSortBy' : 'sortBy', 'sortBy')
    getCuratedGroup(
      curatedGroupId,
      itemsPerPage,
      offset,
      orderBy,
      currentUser.preferences.termId
    ).then(group => {
      if (group) {
        groupStore.setCuratedGroupName(group.name)
        groupStore.setDomain(group.domain)
        groupStore.setOwnerId(group.ownerId)
        groupStore.setReferencingCohortIds(group.referencingCohortIds)
        groupStore.setStudents(group.students)
        groupStore.setTotalStudentCount(group.totalStudentCount)
      }
      resolve(group)
    })
  })
}
