import {each, find, map, split, upperFirst} from 'lodash'
import {useContextStore} from '@/stores/context'
import type {
  BoaUser,
  BoaUserDepartment,
  Department,
  DepartmentMembership,
  DepartmentMembershipRole,
  HasDeptCode,
  PeerAdvisingDepartment
} from '@/lib/types'

export const ADVISING_ROLE_TYPES: DepartmentMembershipRole[] = ['advisor', 'director']

export const PEER_ADVISING_ROLE_TYPES: DepartmentMembershipRole[] = ['peer_advisor', 'peer_advisor_manager']

export function getBoaUserRoles(department: BoaUserDepartment): string[] {
  const roles: string[] = []
  each(department.memberships, (membership: DepartmentMembership) => {
    roles.push(upperFirst(split(membership.role, '_').join(' ')))
  })
  return roles
}

export function findDepartment<T extends HasDeptCode>(departments: T[], deptCode: string): T {
  const department = find(departments, ['deptCode', deptCode])
  if (!department) {
    throw new TypeError(`Invalid deptCode: ${deptCode}`)
  }
  return department
}

export function findMembership(department: BoaUserDepartment, role: DepartmentMembershipRole): DepartmentMembership {
  const membership: DepartmentMembership | undefined = find(department.memberships, ['role', role])
  if (!membership) {
    throw new TypeError(`BOA user does not have role ${role} in department ${department.deptCode}`)
  }
  return membership
}

export function getDeptCodesPerRoles(user: BoaUser, roles: DepartmentMembershipRole[]): string[] {
  return map(getUserDepartmentsWithRoles(user, roles), 'deptCode')
}

export function getUserDepartmentsWithRoles(user: BoaUser, roles: DepartmentMembershipRole[]): BoaUserDepartment[] {
  const result: BoaUserDepartment[] = []
  each(user.departments, (department: BoaUserDepartment) => {
    each(department.memberships, (membership: DepartmentMembership) => {
      if (membership.role && roles.includes(membership.role)) {
        result.push(department)
      }
    })
  })
  return result
}

export function getPeerAdvisingDepartments(berkeleyDepartments: Department[], deptCode: string): PeerAdvisingDepartment[] {
  const berkeleyDepartment: Department = findDepartment(berkeleyDepartments, deptCode)
  return berkeleyDepartment.peerAdvisingDepartments
}

export const isPeerAdvisingRole = (role: DepartmentMembershipRole): boolean => role.startsWith('peer_')

export function myDeptCodes(roles: DepartmentMembershipRole[]): string[] {
  const departments: BoaUserDepartment[] = getUserDepartmentsWithRoles(useContextStore().currentUser, roles)
  return map(departments, 'deptCode')
}
