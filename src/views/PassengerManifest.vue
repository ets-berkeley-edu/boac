<template>
  <div v-if="!contextStore.loading" class="default-margins">
    <div class="align-center d-flex flex-wrap">
      <div class="pr-2">
        <v-icon color="primary" :icon="mdiContacts" size="x-large" />
      </div>
      <h1 id="page-header" class="mb-1 mr-3 text-no-wrap">
        Passenger Manifest
      </h1>
      <div v-if="manifestStore.users.length">
        (<v-btn
          id="download-csv"
          aria-label="Download the users currently shown in Passenger Manifest"
          class="font-size-16 letter-spacing-normal px-0 download-csv text-medium-emphasis"
          color="primary"
          density="compact"
          :disabled="isDownloadingCsv || isFetching || manifestStore.isCreatingNewUser"
          slim
          :text="isDownloadingCsv ? 'Downloading CSV...' : 'CSV download'"
          variant="text"
          @click="() => fetchUsers(true)"
        >
          <template v-if="isDownloadingCsv" #append>
            <v-progress-circular
              color="primary"
              indeterminate
              size="16"
              width="3"
            />
          </template>
        </v-btn>)
      </div>
      <div class="ml-auto">
        <CreateNewBoaUser />
      </div>
    </div>
    <div class="mt-4">
      <SearchAndFilterBoaUsers :fetch-users="fetchUsers" />
    </div>
    <div class="align-center d-flex justify-space-between mt-2 w-100">
      <QuickLinks :fetch-users="fetchUsers" />
      <div v-if="!isFetching && !isNaN(totalUserCount)" class="text-medium-emphasis">
        {{ pluralize('student', totalUserCount) }}
      </div>
    </div>
    <BoaUsers
      v-if="!isFetching && !isNaN(totalUserCount)"
      class="mt-2"
      :fetch-users="fetchUsers"
    />
  </div>
</template>

<script setup lang="ts">
import {get, isNil} from 'lodash'
import {mdiContacts} from '@mdi/js'
import {onMounted, ref} from 'vue'
import {storeToRefs} from 'pinia'
import type {BoaUser} from '@/lib/types'
import {ADVISING_ROLE_TYPES, PEER_ADVISING_ROLE_TYPES, findPeerAdvisingDepartment} from '@/lib/berkeley-department'
import BoaUsers from '@/components/admin/passenger-manifest/BoaUsers.vue'
import CreateNewBoaUser from '@/components/admin/passenger-manifest/CreateNewBoaUser.vue'
import QuickLinks from '@/components/admin/passenger-manifest/QuickLinks.vue'
import SearchAndFilterBoaUsers from '@/components/admin/passenger-manifest/SearchAndFilterBoaUsers.vue'
import {getAdminUsers, getPeerAdvisingUsers, getUserByUid, getUsers} from '@/api/user'
import {normalizeId, pluralize, putFocusNextTick} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {useManifestStore} from '@/stores/manifest'

const contextStore = useContextStore()
const manifestStore = useManifestStore()
const isDownloadingCsv = ref(false)
const {isFetching, totalUserCount} = storeToRefs(manifestStore)

contextStore.loadingStart()

onMounted(() => {
  manifestStore.init().then(() => {
    contextStore.loadingComplete()
    putFocusNextTick('search-user-input')
  })
})

const fetchUsers = (isCsvDownloadRequest?: boolean) => {
  if (!contextStore.loading) {
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
      if (isCsvDownloadRequest) {
        isDownloadingCsv.value = true
      } else {
        manifestStore.setIsFetching(true)
        manifestStore.setUsers([])
      }
      const afterFetchUsers = (users: BoaUser[]) => {
        if (isCsvDownloadRequest) {
          isDownloadingCsv.value = false
        } else {
          manifestStore.setUidBeingEdited(undefined)
          manifestStore.setIsFetching(false)
          manifestStore.setUsers(users)
        }
      }
      const sortBy = manifestStore.sortBy
      const sortDescending = manifestStore.sortDescending
      if (filter.type === 'filter') {
        if (PEER_ADVISING_ROLE_TYPES.includes(filter.role)) {
          let csvFilenamePrefix: string | undefined
          const peerAdvisingDepartmentId = filter.peerAdvisingDepartmentId
          if (isCsvDownloadRequest) {
            csvFilenamePrefix = `BOA-${filter.role}s`
            if (filter.peerAdvisingDepartmentId) {
              const peerAdvisingDepartment = findPeerAdvisingDepartment(
                manifestStore.allBerkeleyDepartments,
                peerAdvisingDepartmentId
              )
              csvFilenamePrefix += `-of-peer-dept-${peerAdvisingDepartment.name}`
            }
          }
          getPeerAdvisingUsers(
            peerAdvisingDepartmentId,
            filter.role,
            sortBy,
            sortDescending,
            filter.status,
            csvFilenamePrefix
          ).then(afterFetchUsers)
        } else if (ADVISING_ROLE_TYPES.includes(filter.role) || isNil(filter.role)) {
          getUsers(
            filter.deptCode,
            filter.role,
            sortBy,
            sortDescending,
            filter.status,
            isCsvDownloadRequest ? normalizeId(`BOA-${filter.role}s-dept-${filter.deptCode}`) : undefined
          ).then(afterFetchUsers)
        } else if (filter.role === 'admin') {
          getAdminUsers(
            sortBy,
            sortDescending,
            filter.status,
            isCsvDownloadRequest ? 'BOA-admin-users' : undefined
          ).then(afterFetchUsers)
        } else {
          throw new TypeError(`Invalid role: ${filter.role}`)
        }
      } else if (filter.type === 'search') {
        if (!searchFirstUser) {
          uidOfUser = manifestStore.uidBeingEdited.uid
        }
        if (uidOfUser) {
          getUserByUid(uidOfUser, true).then(data => afterFetchUsers([data]))
        }
      } else {
        throw new TypeError(`Invalid filter type: ${filter.type}`)
      }
    }
  }
}
</script>

<style scoped>
.download-csv {
  margin-bottom: 2px;
}
</style>
