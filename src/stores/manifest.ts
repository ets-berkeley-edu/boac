import type {StoreDefinition} from 'pinia'
import {defineStore} from 'pinia'
import {each, find, indexOf, size, sortBy} from 'lodash'
import type {BoaUser, BoaUsersFilter, Department, PeerAdvisingDepartment} from '@/lib/types'
import {getDepartments} from '@/api/user'

const DEFAULT_FILTER: BoaUsersFilter = {
  deptCode: undefined,
  peerAdvisingDepartmentId: undefined,
  role: 'advisor',
  searchPhrase: '',
  status: 'active',
  type: 'search'
}

export const useManifestStore: StoreDefinition = defineStore('manifest', {
  state: () => ({
    allBerkeleyDepartments: [] as Department[],
    allPeerAdvisingDepartments: [] as PeerAdvisingDepartment[],
    becomingUid: undefined as string | undefined,
    filter: DEFAULT_FILTER as BoaUsersFilter,
    isCreatingNewUser: false as boolean,
    isFetching: false as boolean,
    sortBy: 'lastName' as string,
    sortDescending: false,
    totalUserCount: NaN as number,
    uidBeingEdited: undefined as string | undefined,
    users: [] as BoaUser[]
  }),
  getters: {
    disabled: (state): boolean => {
      return state.isBecomingUid || state.isFetching
    }
  },
  actions: {
    init(): Promise<void> {
      return new Promise<void>(resolve => {
        this.reset()
        return getDepartments().then(data => {
          this.allBerkeleyDepartments = data
          this.allPeerAdvisingDepartments = []
          each(this.allBerkeleyDepartments, d => {
            each(d.peerAdvisingDepartments, p => this.allPeerAdvisingDepartments.push(p))
          })
          this.allPeerAdvisingDepartments = sortBy(this.allPeerAdvisingDepartments, 'name')
          resolve()
        })
      })
    },
    onUpdateUser(updatedUser: BoaUser) {
      const existingUser: BoaUser | undefined = find(this.users, ['uid', updatedUser.uid])
      if (existingUser) {
        const index: number = indexOf(this.users, existingUser)
        if (index !== -1) {
          this.users.splice(index, 1)
          this.users.splice(index, 0, updatedUser)
        }
      }
    },
    reset() {
      this.becomingUid = undefined
      this.filter = DEFAULT_FILTER
      this.isCreatingNewUser = false
      this.isFetching = false
      this.uidBeingEdited = undefined
    },
    setFilter(filter: BoaUsersFilter) {
      this.filter = filter
    },
    setIsCreatingNewUser(isCreating: boolean) {
      this.isCreatingNewUser = isCreating
    },
    setIsFetching(isFetching: boolean) {
      this.isFetching = isFetching
    },
    setSortBy(sortBy: string) {
      this.sortBy = sortBy
    },
    setSortDescending(sortDescending: boolean) {
      this.sortDescending = sortDescending
    },
    setUidBeingEdited(uid: string) {
      this.uidBeingEdited = uid
    },
    setUsers(users: BoaUser[]) {
      this.users = users
      this.totalUserCount = size(users)
    }
  }
})
