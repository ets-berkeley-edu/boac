<template>
  <v-card
    class="modal-content"
    max-width="500"
    min-width="500"
  >
    <v-card-title>
      <ModalHeader :text="user.id ? user.name : 'Create User'" />
    </v-card-title>
    <v-card-text class="modal-body">
      <div v-if="!user.id" class="align-center d-flex pb-3">
        <label class="font-size-18 mr-2" for="uid-input">UID:</label>
        <v-text-field
          id="uid-input"
          v-model="user.uid"
          hide-details
          maxlength="10"
          max-width="140"
        />
      </div>
      <ManageBoaUserPermissions v-model="user" />
      <ManageBoaUserDepartments v-model="user" :all-berkeley-departments="allBerkeleyDepartments" />
      <SelectBerkeleyDepartment v-model="user" :all-berkeley-departments="allBerkeleyDepartments" />
      <pre>
        {{ user.departments }}
      </pre>
    </v-card-text>
    <v-card-actions class="modal-footer">
      <ProgressButton
        id="save-changes-to-user-profile"
        :action="save"
        :disabled="isSaving || !role || !user.uid"
        :in-progress="isSaving"
        :text="isSaving ? 'Saving' : 'Save'"
      />
      <v-btn
        id="cancel-changes-to-user-profile"
        text="Cancel"
        variant="text"
        @click="cancel"
      />
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import ManageBoaUserDepartments from '@/components/admin/passenger-manifest/ManageBoaUserDepartments.vue'
import ManageBoaUserPermissions from '@/components/admin/passenger-manifest/ManageBoaUserPermissions.vue'
import ModalHeader from '@/components/util/ModalHeader.vue'
import ProgressButton from '@/components/util/ProgressButton.vue'
import SelectBerkeleyDepartment from '@/components/admin/passenger-manifest/SelectBerkeleyDepartment.vue'
import {BoaUser, Department, alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {PropType, ref} from 'vue'
import {createOrUpdateUser} from '@/api/user'

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

const isSaving = ref(false)
const role = ref(undefined)

const cancel = () => {
  props.onCancel()
  alertScreenReader('Canceled')
  putFocusNextTick(user.value.id ? `edit-${user.value.uid}` : 'add-new-user-btn')
}

const save = () => {
  isSaving.value = true
  createOrUpdateUser(user.value).then(() => {
    props.onSave()
    isSaving.value = false
  })
}
</script>
