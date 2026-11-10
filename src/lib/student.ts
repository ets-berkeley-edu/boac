import {get, groupBy, includes, map, orderBy} from 'lodash'
import type {Student} from '@/lib/types'
import {myDeptCodes} from '@/lib/berkeley-department'
import {useContextStore} from '@/stores/context'

export function displayAsAscInactive(student: object) {
  return (
    includes(myDeptCodes(['advisor', 'director']), 'UWASC') &&
    get(student, 'athleticsProfile') &&
    !get(student, 'athleticsProfile.isActiveAsc')
  )
}

export function displayAsCoeInactive(student: object) {
  const isAuthorized = useContextStore().currentUser.isAdmin || includes(myDeptCodes(['advisor', 'director']), 'COENG')
  return isAuthorized && get(student, 'coeProfile') && !get(student, 'coeProfile.isActiveCoe')
}

export function displayCoeAcademicStanding(student: object) {
  const isAuthorized = useContextStore().currentUser.isAdmin || includes(myDeptCodes(['advisor', 'director']), 'COENG')
  return isAuthorized && get(student, 'coeProfile') && get(student, 'coeProfile.acadStatusDescription')
}

// In the Classes section, a year's three terms sit side by side when the text-scaled window width (see
// useTextScaledDisplayWidth) is at least this wide, which is Vuetify's 'lg' breakpoint. Otherwise they stack.
export const TERMS_SIDE_BY_SIDE_MIN_WIDTH = 1400

export function getEnrollmentTermsByYear(student: Student, descending: boolean) {
  const currentEnrollmentTerm = useContextStore().config.currentEnrollmentTerm
  const grouped = groupBy(student.enrollmentTerms, 'academicYear')
  const enrollmentTerms = map(grouped, (terms: object[], year: number) => {
    const semesters = [`Fall ${year - 1}`, `Spring ${year}`, `Summer ${year}`]
    return {
      isOpen: includes(semesters, currentEnrollmentTerm),
      label: year,
      terms
    }
  })
  const orders = descending ? 'desc' : 'asc'
  let enrollmentTermsByYear = orderBy(enrollmentTerms, 'label', orders)
  enrollmentTermsByYear = orderBy(enrollmentTermsByYear, 'label', orders)
  return enrollmentTermsByYear
}
