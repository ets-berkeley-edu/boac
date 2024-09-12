<template>
  <div v-if="!contextStore.loading" class="default-margins">
    <div class="d-flex flex-wrap">
      <div class="align-center d-flex">
        <div class="pr-2">
          <v-icon color="primary" :icon="mdiContacts" size="x-large" />
        </div>
        <h1 id="dept-users-section" class="mb-0 mr-3 page-section-header text-no-wrap">
          Passenger Manifest
        </h1>
        <div class="pr-3">
          <span class="font-size-14 text-medium-emphasis">(<a id="download-boa-users-csv" :href="`${contextStore.config.apiBaseUrl}/api/users/csv`">download</a>)</span>
        </div>
      </div>
      <EditUserProfileModal
        :after-cancel="afterCancelCreateUser"
        :after-update-user="afterCreateUser"
        class="ml-auto"
        :departments="departments"
      />
    </div>
    <Users :departments="departments" :refresh="refreshUsers" />
  </div>
</template>

<script setup>
import EditUserProfileModal from '@/components/admin/EditUserProfileModal'
import Users from '@/components/admin/Users'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {getDepartments} from '@/api/user'
import {mdiContacts} from '@mdi/js'
import {onMounted, ref} from 'vue'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const departments = ref(undefined)
const refreshUsers = ref(false)

contextStore.loadingStart()

onMounted(() => {
  getDepartments(true).then(data => {
    departments.value = data
    contextStore.loadingComplete()
  })
})

const afterCancelCreateUser = () => {
  alertScreenReader('Canceled')
  putFocusNextTick('add-new-user-btn')
}

const afterCreateUser = name => {
  refreshUsers.value = true
  alertScreenReader(`${name} has been added to BOA.`)
  putFocusNextTick('add-new-user-btn')
}
</script>
