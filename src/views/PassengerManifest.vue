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
import {mdiContacts, mdiPlus} from '@mdi/js'
import {nextTick, onMounted, ref} from 'vue'
import {cloneDeep} from 'lodash'
import BoaUsers from '@/components/admin/passenger-manifest/BoaUsers.vue'
import EditUser from '@/components/admin/passenger-manifest/EditUser.vue'
import type {BoaUser, Department} from '@/lib/types'
import {ANONYMOUS_USER, alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {getDepartments} from '@/api/user'

const contextStore = useContextStore()
const allBerkeleyDepartments = ref<Department[]>([])
const isCreatingNewUser = ref(false)
const newUser = ref<BoaUser>(getNewUserTemplate())
const refreshUsers = ref(false)

contextStore.loadingStart()

onMounted(() => {
  getDepartments().then(data => {
    allBerkeleyDepartments.value = data
    contextStore.loadingComplete()
  })
})

function getNewUserTemplate() {
  const user = cloneDeep(ANONYMOUS_USER)
  // Set defaults on new-user object
  user.canAccessAdvisingData = true
  user.canAccessCanvasData = true
  return user
}

const onCancelEditUser = () => {
  isCreatingNewUser.value = false
  alertScreenReader('Canceled')
  nextTick(() => {
    newUser.value = getNewUserTemplate()
    putFocusNextTick('add-new-user-btn')
  })
}

const onCreateUser = (name: string) => {
  isCreatingNewUser.value = false
  newUser.value = getNewUserTemplate()
  refreshUsers.value = true
  alertScreenReader(`${name} has been added to BOA.`)
  putFocusNextTick('add-new-user-btn')
}
</script>
