<template>
  <div>
    <v-btn
      id="add-new-user-btn"
      class="pl-4 pr-4"
      color="primary"
      density="comfortable"
      :disabled="manifestStore.disabled"
      :prepend-icon="mdiPlus"
      text="Add New User"
      @click="() => manifestStore.setIsCreatingNewUser(true)"
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
</template>

<script setup lang="ts">
import {cloneDeep} from 'lodash'
import {mdiPlus} from '@mdi/js'
import {nextTick, ref} from 'vue'
import {storeToRefs} from 'pinia'
import {useManifestStore} from '@/stores/manifest'
import EditUser from '@/components/admin/passenger-manifest/EditUser.vue'
import {ANONYMOUS_USER, alertScreenReader, putFocusNextTick} from '@/lib/utils'
import type {BoaUser} from '@/lib/types'

const manifestStore = useManifestStore()
const {allBerkeleyDepartments, isCreatingNewUser} = storeToRefs(manifestStore)

const newUser = ref<BoaUser>(getNewUserTemplate())
const refreshUsers = ref(false)

function getNewUserTemplate() {
  const user = cloneDeep(ANONYMOUS_USER)
  // Set defaults on new-user object
  user.canAccessAdvisingData = true
  user.canAccessCanvasData = true
  return user
}

const onCancelEditUser = () => {
  manifestStore.setIsCreatingNewUser(false)
  alertScreenReader('Canceled')
  nextTick(() => {
    newUser.value = getNewUserTemplate()
    putFocusNextTick('add-new-user-btn')
  })
}

const onCreateUser = (name: string) => {
  manifestStore.setIsCreatingNewUser(false)
  newUser.value = getNewUserTemplate()
  refreshUsers.value = true
  alertScreenReader(`${name} has been added to BOA.`)
  putFocusNextTick('add-new-user-btn')
}
</script>
