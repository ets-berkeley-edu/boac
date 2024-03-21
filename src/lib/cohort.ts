import {each, get, includes, isEmpty, size, trim} from 'lodash'
import {myDeptCodes} from '@/berkeley'
import {useContextStore} from '@/stores/context'

const isExistingName = (name: string, id?: number) => {
  const currentUser = useContextStore().currentUser
  const all = {
    'curated group': currentUser.myCuratedGroups,
    cohort: currentUser.myCohorts
  }
  let msg = undefined as string | undefined
  each(all, (cohorts, cohortType) => {
    if (msg) {
      return false
    }
    each(cohorts, existing => {
      if (
        (!id || id !== existing.id) &&
        name.toUpperCase() === existing.name.toUpperCase()
        ) {
        msg = `You have an existing ${cohortType} with this name. Please choose a different name.`
        return false
      }
    })
  })
  return msg
}

const isReservedName = (name: string) => {
  const deptCodes = myDeptCodes(['advisor', 'director'])
  return includes(deptCodes, 'UWASC') &&
  includes(['intensive students', 'inactive students'], name.toLowerCase())
}

export function validateCohortName(cohort: {id?: number, name: string}) {
  const name = trim(cohort.name)
  if (isEmpty(name)) {
    return 'Name is required'
  }
  if (size(name) > 255) {
    return 'Name must be 255 characters or fewer'
  }
  if (isReservedName(name)) {
    return `Sorry, '${name}' is a reserved name. Please choose a different name.`
  }
  const msg = isExistingName(name, get(cohort, 'id'))
  return msg || true
}
