import store from '@/store'
import {each, includes, isEmpty, size, trim} from 'lodash'
import {myDeptCodes} from '@/berkeley'

export function validateCohortName(cohort) {
  const name = trim(cohort.name)
  const deptCodes = myDeptCodes(['advisor', 'director'])
  const isReservedName = name =>
    includes(deptCodes, 'UWASC') &&
    includes(['intensive students', 'inactive students'], name.toLowerCase())
  let msg: string | undefined = undefined
  if (isEmpty(name)) {
    msg = 'Required'
  } else if (size(name) > 255) {
    msg = 'Name must be 255 characters or fewer'
  } else if (isReservedName(name)) {
    msg = `Sorry, '${name}' is a reserved name. Please choose a different name.`
  } else {
    const currentUser = store.getters['context/currentUser']
    const all = {
      'curated group': currentUser.myCuratedGroups,
      cohort: currentUser.myCohorts
    }
    each(all, (cohorts, cohortType) => {
      each(cohorts, existing => {
        if (
          (!cohort['id'] || cohort.id !== existing.id) &&
          name.toUpperCase() === existing.name.toUpperCase()
        ) {
          msg = `You have an existing ${cohortType} with this name. Please choose a different name.`
          return false
        }
      })
    })
  }
  return msg
}
