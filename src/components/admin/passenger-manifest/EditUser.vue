<template>
  <v-card
    class="modal-content"
    max-width="600"
    min-width="600"
  >
    <v-card-title class="pb-0">
      <div class="align-end d-flex flex-wrap justify-space-between">
        <ModalHeader :text="user.id ? user.name : 'Create User'" />
        <div v-if="user.id" class="font-size-16 mb-1 mr-2 text-medium-emphasis">
          <span class="font-weight-550">UID:</span> {{ user.uid }}
        </div>
      </div>
      <v-expand-transition>
        <div
          v-show="error"
          id="edit-user-error"
          aria-live="polite"
          class="mb-1 mx-3 text-error font-size-13"
          role="alert"
        >
          {{ error }}
        </div>
      </v-expand-transition>
    </v-card-title>
    <v-card-text class="modal-body">
      <div v-if="!user.id" class="align-center d-flex mb-2">
        <label class="font-size-18 mr-2" for="uid-input">UID:</label>
        <v-text-field
          id="uid-input"
          v-model="user.uid"
          autocomplete="off"
          density="compact"
          hide-details
          maxlength="10"
          max-width="140"
          @keydown.esc="onCancel"
        />
      </div>
      <ManageBoaUserPermissions v-model="user" />
      <ManageBoaUserDepartments v-model="user" class="mt-2" />
      <v-expand-transition>
        <SelectBerkeleyDepartment
          v-if="!isPeerAdvisor(user)"
          v-model="user"
          class="mt-2"
        />
      </v-expand-transition>
      <v-expand-transition>
        <div v-if="user.isAdmin" class="font-size-14 opacity-60 ml-2 mt-1 text-medium-emphasis text-red">
          Uncheck the Admin checkbox to add departments.
        </div>
      </v-expand-transition>
    </v-card-text>
    <v-card-actions class="modal-footer">
      <ProgressButton
        id="save-changes-to-user-profile"
        :action="save"
        :disabled="isSaveButtonDisabled"
        :in-progress="isSaving"
        :text="isSaving ? 'Saving' : 'Save'"
      />
      <v-btn
        id="cancel-changes-to-user-profile"
        text="Cancel"
        variant="text"
        @click="onCancel"
      />
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {computed, ref, watch} from 'vue'
import {each, get, size} from 'lodash'
import type {BoaUser, BoaUserDepartment, DepartmentMembership} from '@/lib/types'
import ManageBoaUserDepartments from '@/components/admin/passenger-manifest/ManageBoaUserDepartments.vue'
import ManageBoaUserPermissions from '@/components/admin/passenger-manifest/ManageBoaUserPermissions.vue'
import ModalHeader from '@/components/util/ModalHeader.vue'
import ProgressButton from '@/components/util/ProgressButton.vue'
import SelectBerkeleyDepartment from '@/components/admin/passenger-manifest/SelectBerkeleyDepartment.vue'
import {createOrUpdateUser} from '@/api/user'
import {isPeerAdvisingRole} from '@/lib/berkeley-department'
import {isPeerAdvisor} from '@/lib/boa-user'

const user = defineModel<BoaUser>({
  required: true,
  type: Object as PropType<BoaUser>
})

const props = defineProps({
  onCancel: {
    default: () => {},
    type: Function
  },
  onSave: {
    default: () => {},
    type: Function
  }
})

const error = ref<string | undefined>()
const isSaving = ref(false)

watch(() => user.value, () => error.value = undefined, {deep: true})

const isSaveButtonDisabled = computed(() => {
  let disabled = false
  const departments = user.value.departments
  const isValidDepartmentCount = user.value.isAdmin || user.value.deletedAt || size(departments)
  if (isSaving.value || !user.value.uid || !isValidDepartmentCount) {
    disabled = true
  } else {
    each(departments, (department: BoaUserDepartment) => {
      disabled = !size(department.memberships) || hasMissingRole(department.memberships)
      return !disabled
    })
  }
  return disabled
})

const hasMissingRole = (memberships: DepartmentMembership[]) => {
  let hasMissing = false
  each(memberships, (membership: DepartmentMembership) => {
    hasMissing = !membership.role || (isPeerAdvisingRole(membership.role) && !membership.peerAdvisingDepartmentId)
    return !hasMissing
  })
  return hasMissing
}

const save = () => {
  isSaving.value = true
  createOrUpdateUser(user.value).then(() => {
    props.onSave()
  }).catch((reason: string) => {
    error.value = get(reason, 'response.data.message') || get(reason, 'message')
  }).finally(() => {
    isSaving.value = false
  })
}
</script>
