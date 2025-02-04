<template>
  <div>
    <v-btn
      v-if="isExistingUser"
      :id="`edit-${profile.uid}`"
      :aria-label="`Edit profile of ${profile.name}`"
      color="primary"
      :disabled="disabled"
      :icon="mdiNoteEditOutline"
      variant="text"
      width="20"
      @click.stop.prevent="openEditUserModal"
    >
    </v-btn>
    <v-btn
      v-if="!isExistingUser"
      id="add-new-user-btn"
      class="pl-4 pr-4 mr-6"
      color="primary"
      :prepend-icon="mdiPlus"
      text="Add New User"
      @click.stop.prevent="openEditUserModal"
    />
    <v-dialog
      v-model="showEditUserModal"
      aria-labelledby="modal-header"
      persistent
    >
      <v-card
        class="modal-content"
        max-width="500"
        min-width="500"
      >
        <FocusLock @keydown.esc="cancel">
          <v-card-title>
            <ModalHeader :text="isExistingUser ? profile.name : 'Create User'" />
          </v-card-title>
          <v-card-text class="modal-body">
            <v-alert
              v-if="size(errors)"
              id="edit-user-error"
              aria-live="polite"
              class="mb-4"
              closable
              density="compact"
              :icon="mdiAlert"
              type="error"
              variant="tonal"
              @click:close="alertScreenReader('Alert dismissed')"
            >
              <span class="font-weight-bold">Error: </span><template v-if="size(errors) === 1">{{ errors[0] }}</template>
              <template v-else>
                <ul class="list-bullets">
                  <li v-for="(error, index) in errors" :key="index">{{ error }}</li>
                </ul>
              </template>
            </v-alert>
            <div v-if="!isExistingUser" class="align-center d-flex pb-3">
              <label class="font-size-18 mr-2" for="uid-input">UID:</label>
              <v-text-field
                id="uid-input"
                v-model="userProfile.uid"
                :error="isUidInvalid"
                hide-details
                maxlength="10"
                max-width="140"
                @keydown.enter.prevent="save"
                @update:model-value="isUidInvalid = false"
              />
            </div>
            <div class="pb-3">
              <div class="d-flex">
                <div class="w-33">
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
            <div v-if="isCoe({departments: memberships}) || userProfile.degreeProgressPermission">
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
            <h4 class="sr-only">Departments</h4>
            <v-card
              v-for="dept in memberships"
              :key="dept.deptCode"
              class="bg-grey-lighten-4 border-md mt-1"
              flat
            >
              <v-card-title class="align-center d-flex">
                <h5 class="text-wrap font-size-16">{{ dept.deptName }} ({{ dept.deptCode }})</h5>
                <v-btn
                  :id="`remove-department-${dept.deptCode}`"
                  :aria-label="`Remove department '${dept.deptName}'`"
                  class="align-self-start bg-grey-lighten-4 ml-auto text-error"
                  density="comfortable"
                  :icon="mdiCloseCircleOutline"
                  title="Remove"
                  variant="flat"
                  @click="() => removeDepartment(dept.deptCode, dept.role)"
                />
              </v-card-title>
              <v-card-text>
                <div class="align-center d-flex pl-8">
                  <label class="font-weight-black mr-2" :for="`select-department-${dept.deptCode}-role`">Role</label>
                  <select
                    :id="`select-department-${dept.deptCode}-role`"
                    v-model="dept.role"
                    class="select-menu select-department-role"
                    :class="{'border border-error border-opacity-100 text-error': includes(map(membershipsMissingRoles, 'deptCode'), dept.deptCode)}"
                    @change="remove(membershipsMissingRoles, {'deptCode': dept.deptCode})"
                  >
                    <option
                      id="department-role-null"
                      :value="null"
                    >
                      Select Role...
                    </option>
                    <option
                      v-for="option in roles"
                      :id="`department-role-${lowerCase(option.value)}`"
                      :key="option.value"
                      :disabled="isRoleOptionDisabled(dept.deptCode, option.value)"
                      :value="option.value"
                    >
                      {{ option.text }}
                    </option>
                  </select>
                </div>
                <v-expand-transition>
                  <div v-show="dept.role !== 'peer_advisor_manager'" class="pl-8 pt-1">
                    <v-checkbox
                      :id="`is-automate-membership-${dept.deptCode}`"
                      v-model="dept.automateMembership"
                      class="automate-membership-checkbox"
                      color="primary"
                      density="compact"
                      hide-details
                    >
                      <template #label>
                        <span class="pl-1">Automated</span>
                      </template>
                    </v-checkbox>
                  </div>
                </v-expand-transition>
              </v-card-text>
            </v-card>
            <div v-if="memberships.length >= 3">
              <span class="text-info"><v-icon class="mb-1" :icon="mdiCheckBold" /> Three departments is enough!</span>
            </div>
            <div v-if="memberships.length < 3" class="pt-2">
              <select
                id="department-select-list"
                v-model="deptCode"
                aria-label="Department"
                class="select-menu w-100"
                @change="addDepartment"
              >
                <option id="department-null" :value="undefined">
                  Select Department...
                </option>
                <option
                  v-for="option in departmentOptions"
                  :id="`department-option-${lowerCase(option.value)}`"
                  :key="option.value"
                  :disabled="isDepartmentOptionDisabled(option.value)"
                  :value="option.value"
                >
                  {{ option.text }}
                </option>
              </select>
            </div>
          </v-card-text>
          <v-card-actions class="modal-footer">
            <ProgressButton
              id="save-changes-to-user-profile"
              :action="save"
              :disabled="isSaving || isUidInvalid || !userProfile.uid || memberships.findIndex(d => !d.role) >= 0"
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
import {alertScreenReader, oxfordJoin, putFocusNextTick, scrollTo} from '@/lib/utils'
import {computed, ref} from 'vue'
import {createOrUpdateUser} from '@/api/user'
import {filter as _filter, each, find, get, includes, isNil, lowerCase, map, remove, size} from 'lodash'
import {isCoe} from '@/berkeley'
import {mdiAlert, mdiCheckBold, mdiCloseCircleOutline, mdiNoteEditOutline, mdiPlus} from '@mdi/js'

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
  disabled: {
    required: true,
    type: Boolean
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
const errors = ref([])
const isDeleted = ref(undefined)
const isSaving = ref(false)
const isUidInvalid = ref(false)
const membershipsMissingRoles = ref([])
const memberships = ref([])
const showEditUserModal = ref(false)
const userProfile = ref({})
const degreeProgressPermissionItems = [
  {value: 'read', text: 'Read-only'},
  {value: 'read_write', text: 'Read and write'}
]
const roles = [
  {value: 'advisor', text: 'Advisor'},
  {value: 'director', text: 'Director'},
  {value: 'peer_advisor_manager', text: 'Peer Advisor Manager'}
]

const isExistingUser = computed(() => {
  return !!props.profile.id
})

const addDepartment = () => {
  if (deptCode.value) {
    const dept = find(props.departments, ['deptCode', deptCode.value])
    memberships.value.push({
      deptCode: dept.deptCode,
      deptName: dept.deptName,
      role: null,
      automateMembership: true
    })
    const option = find(departmentOptions.value, ['value', deptCode.value])
    option.disabled = isDepartmentOptionDisabled(deptCode.value)
    deptCode.value = undefined
  }
}

const cancel = () => {
  closeModal()
  props.afterCancel(props.profile)
}

const clearErrors = () => {
  errors.value = []
  isUidInvalid.value = false
  membershipsMissingRoles.value = []
}

const closeModal = () => {
  clearErrors()
  showEditUserModal.value = false
  userProfile.value = {}
  memberships.value = []
}

const isDepartmentOptionDisabled = deptCode => {
  const existing_roles = map(_filter(memberships.value, ['deptCode', deptCode]), 'role')
  return existing_roles.length === 2 && existing_roles.includes('peer_advisor_manager')
}

const isRoleOptionDisabled = (deptCode, role) => {
  let isDisabled = false
  const memberships_per_dept_code = _filter(memberships.value, ['deptCode', deptCode])
  if (memberships_per_dept_code.length > 1) {
    const existing_roles = map(memberships_per_dept_code, 'role')
    if (['advisor', 'director'].includes(role)) {
      isDisabled = existing_roles.includes('advisor') || existing_roles.includes('director')
    } else if (role === 'peer_advisor_manager') {
      isDisabled = existing_roles.includes('peer_advisor_manager')
    }
  }
  return isDisabled
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
        deptCode: d.deptCode,
        deptName: d.deptName,
        role: d.role,
      })
    }
  })
  each(props.profile.peerAdvisingDepartments, d => {
    memberships.value.push({
      automateMembership: d.automateMembership,
      deptCode: d.universityDeptCode,
      deptName: d.universityDeptName,
      role: d.roleType,
    })
  })
  departmentOptions.value = []
  each(props.departments, d => {
    departmentOptions.value.push({
      disabled: isDepartmentOptionDisabled(d.deptCode),
      text: d.deptName,
      value: d.deptCode
    })
  })
  showEditUserModal.value = true
  putFocusNextTick(props.profile.uid ? 'is-admin' : 'uid-input')
}

const removeDepartment = (deptCode, role) => {
  const indexOf = memberships.value.findIndex(d => d.deptCode === deptCode && d.role === role)
  const option = find(departmentOptions.value, ['value', deptCode])
  memberships.value.splice(indexOf, 1)
  option.disabled = false
}

const save = () => {
  clearErrors()
  membershipsMissingRoles.value = _filter(memberships.value, r => isNil(r.role))
  if (!userProfile.value.uid) {
    errors.value.push('UID is required')
    isUidInvalid.value = true
  } if (membershipsMissingRoles.value.length) {
    const deptNames = map(membershipsMissingRoles.value, 'deptName')
    errors.value.push(`Please specify role for ${oxfordJoin(deptNames)}`)
  }
  if (!isUidInvalid.value && !membershipsMissingRoles.value.length) {
    isSaving.value = true
    // If no change in deleted status then do not update 'deleted_at' in the database.
    const deleteAction = isDeleted.value === !!props.profile.deletedAt ? null : isDeleted.value
    createOrUpdateUser(userProfile.value, memberships.value, deleteAction).then(() => {
      props.afterUpdateUser(props.profile)
      closeModal()
    }).catch(error => {
      const message = get(error, 'response.data.message', error)
      errors.value.push(message)
      if (includes(message, 'UID')) {
        isUidInvalid.value = true
      }
    }).finally(() => {
      isSaving.value = false
      if (size(errors.value)) {
        scrollTo('edit-user-error')
      }
    })
  }
}
</script>

<style scoped>
.select-department-role {
  background-color: rgb(var(--v-theme-surface));
  min-width: 120px;
  z-index: 1;
}
</style>

<style>
/* eslint-disable-next-line vue-scoped-css/no-unused-selector */
.automate-membership-checkbox .v-label {
  opacity: var(--v-high-emphasis-opacity) !important;
}
</style>
