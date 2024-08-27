<template>
  <div>
    <v-btn
      v-if="isExistingUser"
      :id="`edit-${profile.uid}`"
      :aria-label="`Edit profile of ${profile.name}`"
      color="primary"
      :icon="mdiNoteEditOutline"
      variant="text"
      width="20"
      @click="openEditUserModal"
    >
    </v-btn>
    <v-btn
      v-if="!isExistingUser"
      id="add-new-user-btn"
      class="pl-4 pr-4 mr-6"
      color="primary"
      :prepend-icon="mdiPlus"
      text="Add New User"
      @click="openEditUserModal"
    />
    <v-dialog
      v-model="showEditUserModal"
      aria-labelledby="modal-header"
      persistent
    >
      <v-card
        class="modal-content"
        max-width="600"
        min-width="600"
      >
        <FocusLock @keydown.esc="cancel">
          <v-card-title>
            <ModalHeader :text="isExistingUser ? profile.name : 'Create User'" />
          </v-card-title>
          <v-card-text class="modal-body">
            <div
              v-if="error"
              class="mb-2 mt-1 text-error"
              aria-live="polite"
              role="alert"
            >
              <span class="font-weight-bolder text-error">Error: {{ error }}</span>
            </div>
            <div v-if="!isExistingUser" class="align-items-center pb-3">
              <label for="uid-input" class="sr-only">U I D </label>
              <v-text-field
                id="uid-input"
                v-model="userProfile.uid"
                density="compact"
                hide-details
                label="UID"
                variant="outlined"
                width="50%"
              />
            </div>
            <div class="pb-3">
              <div class="d-flex">
                <div class="w-50">
                  <v-checkbox
                    id="is-admin"
                    v-model="userProfile.isAdmin"
                    density="compact"
                    label="Admin"
                    color="primary"
                    hide-details="true"
                  />
                  <v-checkbox
                    id="is-blocked"
                    v-model="userProfile.isBlocked"
                    density="compact"
                    color="primary"
                    label="Blocked"
                    hide-details="true"
                  />
                  <v-checkbox
                    v-if="profile.id"
                    id="is-deleted"
                    v-model="isDeleted"
                    density="compact"
                    color="primary"
                    label="Deleted"
                    hide-details="true"
                  />
                </div>
                <div>
                  <v-checkbox
                    id="can-access-canvas-data"
                    v-model="userProfile.canAccessCanvasData"
                    density="compact"
                    color="primary"
                    label="Canvas Data"
                    hide-details="true"
                  />
                  <v-checkbox
                    id="can-access-advising-data"
                    v-model="userProfile.canAccessAdvisingData"
                    density="compact"
                    color="primary"
                    label="Notes and Appointments"
                    hide-details="true"
                  />
                </div>
              </div>
            </div>
            <div
              v-if="isCoe({departments: memberships}) || userProfile.degreeProgressPermission"
              class="pb-3"
            >
              <hr class="mb-3" />
              <label class="font-weight-black" for="degree-progress-permission-select">Degree Progress Permission</label>
              <div class="mt-1">
                <select
                  id="degree-progress-permission-select"
                  v-model="userProfile.degreeProgressPermission"
                  class="select-menu w-50"
                >
                  <option id="department-null" :value="null">Select...</option>
                  <option
                    v-for="option in degreeProgressPermissionItems"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.text }}
                  </option>
                </select>
              </div>
              <div class="mt-1">
                <v-checkbox
                  id="automate-degree-progress-permission"
                  v-model="userProfile.automateDegreeProgressPermission"
                  density="compact"
                  color="primary"
                  label="Automate Degree Progress permissions"
                  hide-details="true"
                />
              </div>
            </div>
            <h4 class="font-size-18">Departments</h4>
            <div
              v-for="dept in memberships"
              :key="dept.code"
              class="pt-2"
            >
              <div class="align-center d-flex">
                <h5 class="font-size-16">{{ dept.name }} ({{ dept.code }})</h5>
                <v-btn
                  :id="`remove-department-${dept.code}`"
                  :aria-label="`Remove department '${dept.name}'`"
                  class="px-0 text-error"
                  :icon="mdiCloseCircleOutline"
                  variant="flat"
                  @click="() => removeDepartment(dept.code)"
                />
              </div>
              <div class="w-100">
                <div class="align-center d-flex pl-8">
                  <label class="font-weight-black mr-2" :for="`select-department-${dept.code}-role`">Role:</label>
                  <select
                    :id="`select-department-${dept.code}-role`"
                    v-model="dept.role"
                    class="select-menu w-25"
                  >
                    <option
                      id="department-role-null"
                      :value="null"
                    >
                      Select...
                    </option>
                    <option
                      v-for="option in roles"
                      :id="`department-role-${lowerCase(option.value)}`"
                      :key="option.value"
                      :value="option.value"
                    >
                      {{ option.text }}
                    </option>
                  </select>
                </div>
                <div class="pl-7">
                  <v-checkbox
                    :id="`is-automate-membership-${dept.code}`"
                    v-model="dept.automateMembership"
                    density="compact"
                    color="primary"
                    label="Automated"
                    hide-details
                  />
                </div>
              </div>
            </div>
            <div v-if="memberships.length >= 3">
              <span class="text-info"><v-icon class="mb-1" :icon="mdiCheckBold" /> Three departments is enough!</span>
            </div>
            <div v-if="memberships.length < 3" class="py-3 w-75">
              <select
                id="department-select-list"
                v-model="deptCode"
                class="select-menu w-100"
                @change="addDepartment"
              >
                <option id="department-null" :value="undefined">
                  Select...
                </option>
                <option
                  v-for="option in departmentOptions"
                  :id="`department-option-${lowerCase(option.value)}`"
                  :key="option.value"
                  :disabled="memberships.findIndex(d => d.code === option.value) >= 0"
                  :value="option.value"
                >
                  {{ option.text }}
                </option>
              </select>
            </div>
          </v-card-text>
          <hr />
          <v-card-actions class="modal-footer">
            <ProgressButton
              id="save-changes-to-user-profile"
              :action="save"
              :disabled="isSaving || !userProfile.uid || memberships.findIndex(d => !d.role) >= 0"
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
        </FocusLock>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import FocusLock from 'vue-focus-lock'
import ModalHeader from '@/components/util/ModalHeader'
import ProgressButton from '@/components/util/ProgressButton.vue'
import {computed, ref} from 'vue'
import {createOrUpdateUser} from '@/api/user'
import {each, filter as _filter, find, get, isNil, map} from 'lodash'
import {isCoe} from '@/berkeley'
import {lowerCase} from 'lodash'
import {mdiCloseCircleOutline} from '@mdi/js'
import {mdiCheckBold} from '@mdi/js'
import {mdiNoteEditOutline} from '@mdi/js'
import {mdiPlus} from '@mdi/js'
import {oxfordJoin, putFocusNextTick} from '@/lib/utils'

const props = defineProps({
  afterCancel: {
    required: true,
    type: Function
  },
  afterUpdateUser: {
    required: true,
    type: Function
  },
  departments: {
    required: true,
    type: Array
  },
  profile: {
    default: () => ({
      canAccessAdvisingData: true,
      canAccessCanvasData: true,
      departments: [],
      isAdmin: false,
      isBlocked: false
    }),
    type: Object
  }
})

const departmentOptions = ref(undefined)
const deptCode = ref(undefined)
const error = ref(undefined)
const isDeleted = ref(undefined)
const isSaving = ref(false)
const memberships = ref([])
const showEditUserModal = ref(false)
const userProfile = ref({})
const degreeProgressPermissionItems = [
  {value: 'read', text: 'Read-only'},
  {value: 'read_write', text: 'Read and write'}
]
const roles = [
  {value: 'advisor', text: 'Advisor'},
  {value: 'director', text: 'Director'}
]

const isExistingUser = computed(() => {
  return !!props.profile.id
})

const addDepartment = () => {
  if (deptCode.value) {
    const dept = find(props.departments, ['code', deptCode.value])
    memberships.value.push({
      code: dept.code,
      name: dept.name,
      role: null,
      automateMembership: true
    })
    const option = find(departmentOptions.value, ['value', deptCode.value])
    option.disabled = true
    deptCode.value = undefined
  }
}

const cancel = () => {
  closeModal()
  props.afterCancel(props.profile)
}

const closeModal = () => {
  showEditUserModal.value = false
  error.value = undefined
  userProfile.value = {}
  memberships.value = []
}

const openEditUserModal = () => {
  userProfile.value = {
    id: props.profile.id,
    uid: props.profile.uid,
    name: props.profile.name,
    automateDegreeProgressPermission: props.profile.automateDegreeProgressPermission || false,
    canAccessAdvisingData: props.profile.canAccessAdvisingData,
    canAccessCanvasData: props.profile.canAccessCanvasData,
    degreeProgressPermission: props.profile.degreeProgressPermission || null,
    departments: [],
    isAdmin: props.profile.isAdmin,
    isBlocked: props.profile.isBlocked
  }
  isDeleted.value = !!props.profile.deletedAt
  memberships.value = []
  each(props.profile.departments, d => {
    if (d.role) {
      memberships.value.push({
        automateMembership: d.automateMembership,
        code: d.code,
        name: d.name,
        role: d.role,
      })
    }
  })
  departmentOptions.value = []
  each(props.departments, d => {
    departmentOptions.value.push({
      disabled: !!find(memberships.value, ['code', d.code]),
      value: d.code,
      text: d.name
    })
  })
  showEditUserModal.value = true
  putFocusNextTick(props.profile.uid ? 'is-admin' : 'uid-input')
}

const removeDepartment = deptCode => {
  let indexOf = memberships.value.findIndex(d => d.code === deptCode)
  memberships.value.splice(indexOf, 1)
  const option = find(departmentOptions.value, ['value', deptCode])
  option.disabled = false
}

const save = () => {
  const undefinedRoles = _filter(memberships.value, r => isNil(r.role))
  if (undefinedRoles.length) {
    const deptNames = map(undefinedRoles, 'name')
    error.value = `Please specify role for ${oxfordJoin(deptNames)}`
  } else {
    isSaving.value = true
    // If no change in deleted status then do not update 'deleted_at' in the database.
    const deleteAction = isDeleted.value === !!props.profile.deletedAt ? null : isDeleted.value
    createOrUpdateUser(userProfile.value, memberships.value, deleteAction).then(() => {
      props.afterUpdateUser(props.profile)
      closeModal()
    }).catch(error => {
      error.value = get(error, 'response.data.message') || error
    }).finally(() => {
      isSaving.value = false
    })
  }
}
</script>
