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
      <EditUserProfileModal
        v-model="newUser"
        :after-save="afterCreateUser"
        :all-berkeley-departments="allBerkeleyDepartments"
        class="ml-auto"
        :disabled="false"
      />
    </div>
    <Users :all-berkeley-departments="allBerkeleyDepartments" :refresh="refreshUsers" />
  </div>
</template>

<script setup lang="ts">
import EditUserProfileModal from '@/components/admin/EditUserProfileModal.vue'
import Users from '@/components/admin/Users.vue'
import {ANONYMOUS_USER, BoaUser, Department, alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {mdiContacts} from '@mdi/js'
import {onMounted, ref} from 'vue'
import {useContextStore} from '@/stores/context'
import {cloneDeep} from 'lodash'
import {getDepartments} from '@/api/user'

const contextStore = useContextStore()
const allBerkeleyDepartments = ref<Department[] | undefined>(undefined)
const newUser = ref<BoaUser>(cloneDeep<BoaUser>(ANONYMOUS_USER))
const refreshUsers = ref(false)

contextStore.loadingStart()

onMounted(() => {
  getDepartments().then(data => {
    allBerkeleyDepartments.value = data
    contextStore.loadingComplete()
  })
})

const afterCreateUser = name => {
  newUser.value = cloneDeep(ANONYMOUS_USER)
  refreshUsers.value = true
  alertScreenReader(`${name} has been added to BOA.`)
  putFocusNextTick('add-new-user-btn')
}
</script>
