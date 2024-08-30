<template>
  <div v-if="!contextStore.loading" class="default-margins">
    <div class="align-center d-flex py-2">
      <div class="pr-2">
        <v-icon color="primary" :icon="mdiContacts" size="x-large" />
      </div>
      <h1 id="dept-users-section" class="mb-0 mr-3 page-section-header">
        Passenger Manifest
      </h1>
      <div>
        <span class="font-size-14 text-black-50">(<a id="download-boa-users-csv" :href="`${contextStore.config.apiBaseUrl}/api/users/csv`">download</a>)</span>
      </div>
      <div class="flex-grow-1 text-right">
        <EditUserProfileModal
          :after-cancel="afterCancelCreateUser"
          :after-update-user="afterCreateUser"
          :departments="departments"
        />
      </div>
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

const departments = ref(undefined)
const refreshUsers = ref(false)

const contextStore = useContextStore()
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
