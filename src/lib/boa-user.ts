import {map} from 'lodash'
import type {BoaUser, BoaUserDepartment} from '@/lib/types'
import {getUserDepartmentsWithRoles} from '@/lib/berkeley-department'

export function isAdvisor(user: BoaUser) {
  return !!getUserDepartmentsWithRoles(user, ['advisor']).length
}

export function isCoe(user: BoaUser): boolean {
  const departments: BoaUserDepartment[] = getUserDepartmentsWithRoles(user, ['advisor', 'director'])
  return map(departments, 'deptCode').includes('COENG')
}

export function isDirector(user: BoaUser): boolean {
  return !!getUserDepartmentsWithRoles(user, ['director']).length
}

export function isPeerAdvisor(user: BoaUser): boolean {
  const departments: BoaUserDepartment[] = getUserDepartmentsWithRoles(user, ['peer_advisor'])
  return !!map(departments, 'deptCode').length
}

export function isPeerAdvisorManager(user: BoaUser) {
  const departments: BoaUserDepartment[] = getUserDepartmentsWithRoles(user, ['peer_advisor_manager'])
  return !!map(departments, 'deptCode').length
}
