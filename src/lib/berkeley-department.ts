import {capitalize, each, find, map, split, uniq, upperFirst} from 'lodash'
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

export function findPeerAdvisingDepartment(
  berkeleyDepartments: Department[],
  peerAdvisingDepartmentId: number
): PeerAdvisingDepartment {
  let peerAdvisingDepartment: PeerAdvisingDepartment | undefined
  each(berkeleyDepartments, d => {
    each(d.peerAdvisingDepartments || [], p => {
      if (p.id === peerAdvisingDepartmentId) {
        peerAdvisingDepartment = p
        return true
      }
    })
    return !!peerAdvisingDepartment
  })
  if (!peerAdvisingDepartment) {
    throw new TypeError(`No Peer Advising Department found with ID ${peerAdvisingDepartmentId}`)
  }
  return peerAdvisingDepartment
}

export function getPeerAdvisorDepartmentMembership(user: BoaUser, role: DepartmentMembershipRole): DepartmentMembership {
  let departmentMembership: DepartmentMembership | undefined
  each(user.departments, (department: BoaUserDepartment) => {
    each(department.memberships, (membership: DepartmentMembership) => {
      if (role === membership.role) {
        departmentMembership = membership
      }
      return !!departmentMembership
    })
  })
  if (!departmentMembership) {
    throw new Error(`User ${user.uid} is NOT a ${role} in any Peer Advising Department.`)
  }
  return departmentMembership
}

export function getDeptCodesPerRoles(user: BoaUser, roles: DepartmentMembershipRole[]): string[] {
  return map(getUserDepartmentsWithRoles(user, roles), 'deptCode')
}

export function getDistinctRoleNames(memberships: DepartmentMembership[]): string[] {
  const roleNames: string[] = []
  each(memberships, membership => {
    let role = map(split(membership.role, '_'), word => capitalize(word)).join(' ')
    if (membership.peerAdvisingDepartmentName) {
      role += ` (${membership.peerAdvisingDepartmentName})`
    }
    roleNames.push(role)
  })
  return uniq(roleNames)
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
