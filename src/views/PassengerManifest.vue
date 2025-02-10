<template>
  <div v-if="!contextStore.loading" class="default-margins">
    <div class="d-flex flex-wrap">
      <div class="align-center d-flex">
        <div class="pr-2">
          <v-icon color="primary" :icon="mdiContacts" size="x-large" />
        </div>
        <h1 id="page-header" class="mb-1 mr-3 text-no-wrap">
          Passenger Manifest
        </h1>
        <div class="pr-3">
          <span class="font-size-14 text-medium-emphasis">
            (<a id="download-boa-users-csv" aria-label="Download Passenger Manifest" :href="`${contextStore.config.apiBaseUrl}/api/users/csv`">download</a>)
          </span>
        </div>
      </div>
      <div class="ml-auto">
        <v-btn
          id="add-new-user-btn"
          class="pl-4 pr-4 mr-6"
          color="primary"
          :prepend-icon="mdiPlus"
          text="Add New User"
          @click="() => isCreatingNewUser = true"
        />
        <v-dialog
          v-model="isCreatingNewUser"
          aria-labelledby="modal-header"
          persistent
        >
          <EditUser
            v-model="newUser"
            :all-berkeley-departments="allBerkeleyDepartments"
            :is-dialog-open="isCreatingNewUser"
            :on-cancel="onCancelEditUser"
            :on-save="onCreateUser"
          />
        </v-dialog>
      </div>
    </div>
    <BoaUsers
      :all-berkeley-departments="allBerkeleyDepartments"
      :refresh="refreshUsers"
    />
  </div>
</template>

<script setup lang="ts">
import BoaUsers from '@/components/admin/passenger-manifest/BoaUsers.vue'
import EditUser from '@/components/admin/passenger-manifest/EditUser.vue'
import {ANONYMOUS_USER, BoaUser, Department, alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {mdiContacts, mdiPlus} from '@mdi/js'
import {onMounted, ref} from 'vue'
import {useContextStore} from '@/stores/context'
import {cloneDeep} from 'lodash'
import {getDepartments} from '@/api/user'

const contextStore = useContextStore()
const allBerkeleyDepartments = ref<Department[]>([])
const isCreatingNewUser = ref(false)
const newUser = ref<BoaUser>(cloneDeep<BoaUser>(ANONYMOUS_USER))
const refreshUsers = ref(false)

contextStore.loadingStart()

onMounted(() => {
  getDepartments().then(data => {
    allBerkeleyDepartments.value = data
    contextStore.loadingComplete()
  })
})

const onCancelEditUser = () => {
  isCreatingNewUser.value = false
  alertScreenReader('Canceled')
  newUser.value = cloneDeep(ANONYMOUS_USER)
  putFocusNextTick('add-new-user-btn')
}

const onCreateUser = name => {
  isCreatingNewUser.value = false
  newUser.value = cloneDeep(ANONYMOUS_USER)
  refreshUsers.value = true
  alertScreenReader(`${name} has been added to BOA.`)
  putFocusNextTick('add-new-user-btn')
}
</script>
