import {each, find, map, split, upperFirst} from 'lodash'
import {useContextStore} from '@/stores/context'
import {BoaUser, BoaUserDepartment, Department, DepartmentMembership, DepartmentMembershipRole} from '@/lib/types'

export function getBoaUserRoles(department: BoaUserDepartment): string[] {
  const roles: string[] = []
  each(department.memberships, (membership: DepartmentMembership) => {
    roles.push(upperFirst(split(membership.role, '_').join(' ')))
  })
  return roles
}

export function getBerkeleyDepartment(allBerkeleyDepartments: Department[], deptCode: string): Department {
  const department = find(allBerkeleyDepartments, ['deptCode', deptCode])
  if (!department) {
    throw new TypeError('Invalid deptCode: ' + deptCode)
  }
  return department
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

export function hasPeerAdvisingDepartments(berkeleyDepartments: Department[], deptCode: string): boolean {
  const berkeleyDepartment = getBerkeleyDepartment(berkeleyDepartments, deptCode)
  return !!berkeleyDepartment.peerAdvisingDepartments?.length
}

export function myDeptCodes(roles: DepartmentMembershipRole[]): string[] {
  const departments: BoaUserDepartment[] = getUserDepartmentsWithRoles(useContextStore().currentUser, roles)
  return map(departments, 'deptCode')
}
