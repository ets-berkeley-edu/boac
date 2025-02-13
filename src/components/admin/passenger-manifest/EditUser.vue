<template>
  <v-card
    class="modal-content"
    max-width="500"
    min-width="500"
  >
    <v-card-title class="pb-0">
      <ModalHeader :text="user.id ? user.name : 'Create User'" />
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
      <ManageBoaUserDepartments v-model="user" :all-berkeley-departments="allBerkeleyDepartments" />
      <v-expand-transition>
        <SelectBerkeleyDepartment
          v-show="!isPeerAdvisor(user)"
          v-model="user"
          :all-berkeley-departments="allBerkeleyDepartments"
        />
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
import ManageBoaUserDepartments from '@/components/admin/passenger-manifest/ManageBoaUserDepartments.vue'
import ManageBoaUserPermissions from '@/components/admin/passenger-manifest/ManageBoaUserPermissions.vue'
import ModalHeader from '@/components/util/ModalHeader.vue'
import ProgressButton from '@/components/util/ProgressButton.vue'
import SelectBerkeleyDepartment from '@/components/admin/passenger-manifest/SelectBerkeleyDepartment.vue'
import type {BoaUser, BoaUserDepartment, Department, DepartmentMembership} from '@/lib/types'
import {createOrUpdateUser} from '@/api/user'
import {isPeerAdvisingRole} from '@/lib/berkeley-department'
import {isPeerAdvisor} from '@/lib/boa-user'

const user = defineModel<BoaUser>({
  required: true,
  type: Object as PropType<BoaUser>
})

const props = defineProps({
  allBerkeleyDepartments: {
    required: true,
    type: Array as PropType<Array<Department>>
  },
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
  if (isSaving.value || !user.value.uid || !size(departments)) {
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
