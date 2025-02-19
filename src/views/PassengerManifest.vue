<template>
  <div v-if="!contextStore.loading" class="default-margins">
    <div class="align-center d-flex flex-wrap">
      <div class="pr-2">
        <v-icon color="primary" :icon="mdiContacts" size="x-large" />
      </div>
      <h1 id="page-header" class="mb-1 mr-3 text-no-wrap">
        Passenger Manifest
      </h1>
      <div>
        <span class="font-size-14 text-medium-emphasis">
          (<a id="download-boa-users-csv" aria-label="Download Passenger Manifest" :href="`${contextStore.config.apiBaseUrl}/api/users/csv`">CSV download</a>)
        </span>
      </div>
      <div class="ml-auto">
        <CreateNewBoaUser />
      </div>
    </div>
    <div class="mt-4">
      <SearchAndFilterBoaUsers :fetch-users="fetchUsers" />
    </div>
    <div class="mt-2">
      <QuickLinks :fetch-users="fetchUsers" />
    </div>
    <BoaUsers
      v-if="!isFetching && !isNaN(totalUserCount)"
      class="mt-2"
      :fetch-users="fetchUsers"
    />
  </div>
</template>

<script setup lang="ts">
import {get} from 'lodash'
import {mdiContacts} from '@mdi/js'
import {onMounted} from 'vue'
import {storeToRefs} from 'pinia'
import type {BoaUser} from '@/lib/types'
import BoaUsers from '@/components/admin/passenger-manifest/BoaUsers.vue'
import CreateNewBoaUser from '@/components/admin/passenger-manifest/CreateNewBoaUser.vue'
import QuickLinks from '@/components/admin/passenger-manifest/QuickLinks.vue'
import SearchAndFilterBoaUsers from '@/components/admin/passenger-manifest/SearchAndFilterBoaUsers.vue'
import {ADVISING_ROLE_TYPES, PEER_ADVISING_ROLE_TYPES} from '@/lib/berkeley-department'
import {getAdminUsers, getPeerAdvisingUsers, getUserByUid, getUsers} from '@/api/user'
import {putFocusNextTick} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {useManifestStore} from '@/stores/manifest'

const contextStore = useContextStore()
const manifestStore = useManifestStore()
const {isFetching, totalUserCount} = storeToRefs(manifestStore)

contextStore.loadingStart()

onMounted(() => {
  manifestStore.init().then(() => {
    contextStore.loadingComplete()
    putFocusNextTick('search-user-input')
  })
})

const fetchUsers = () => {
  const filter = manifestStore.filter
  let isValidSelection = (filter.type !== 'search') || get(manifestStore.uidBeingEdited, 'uid')
  let searchFirstUser: boolean = false
  let uidOfUser: string | undefined = undefined

  if (!isValidSelection && manifestStore.users.length === 1 && filter.type === 'search') {
    isValidSelection = manifestStore.users[0].uid
    uidOfUser = manifestStore.users[0].uid
    searchFirstUser = true
  }
  if (isValidSelection) {
    manifestStore.setIsFetching(true)
    manifestStore.setUsers([])
    const afterFetchUsers = (users: BoaUser[]) => {
      manifestStore.setUidBeingEdited(undefined)
      manifestStore.setIsFetching(false)
      manifestStore.setUsers(users)
    }
    const sortBy = manifestStore.sortBy
    const sortDescending = manifestStore.sortDescending
    if (filter.type === 'filter') {
      if (PEER_ADVISING_ROLE_TYPES.includes(filter.role)) {
        getPeerAdvisingUsers(
          filter.peerAdvisingDepartmentId,
          filter.role,
          sortBy,
          sortDescending,
          filter.status
        ).then(afterFetchUsers)
      } else if (ADVISING_ROLE_TYPES.includes(filter.role)) {
        getUsers(
          filter.deptCode,
          filter.role,
          sortBy,
          sortDescending,
          filter.status
        ).then(afterFetchUsers)
      } else if (filter.role === 'admin') {
        getAdminUsers(sortBy, sortDescending, filter.status).then(afterFetchUsers)
      } else {
        throw new TypeError(`Invalid role: ${filter.role}`)
      }
    } else if (filter.type === 'search') {
      if (!searchFirstUser) {
        uidOfUser = manifestStore.uidBeingEdited.uid
      }
      if (uidOfUser) {
        getUserByUid(uidOfUser, false).then(data => afterFetchUsers([data]))
      }
    } else {
      throw new TypeError(`Invalid filter type: ${filter.type}`)
    }
  }
}
</script>
