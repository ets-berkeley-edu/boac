<template>
  <div>
    <v-btn
      v-if="user.id"
      :id="`edit-${user.uid}`"
      :aria-label="`Edit profile of ${user.name}`"
      color="primary"
      :icon="mdiNoteEditOutline"
      variant="text"
      width="20"
      @click.stop.prevent="openEditUserModal"
    >
    </v-btn>
    <v-btn
      v-if="!user.id"
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
            <ModalHeader :text="user.id ? user.name : 'Create User'" />
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
            <div v-if="!user.id" class="align-center d-flex pb-3">
              <label class="font-size-18 mr-2" for="uid-input">UID:</label>
              <v-text-field
                id="uid-input"
                v-model="user.uid"
                hide-details
                maxlength="10"
                max-width="140"
                @keydown.enter.prevent="save"
              />
            </div>
            <div class="pb-3">
              <div class="d-flex">
                <div class="w-33">
                  <v-checkbox
                    id="is-admin"
                    v-model="user.isAdmin"
                    density="compact"
                    label="Admin"
                    color="primary"
                    :hide-details="true"
                  />
                  <v-checkbox
                    id="is-blocked"
                    v-model="user.isBlocked"
                    density="compact"
                    color="primary"
                    label="Blocked"
                    :hide-details="true"
                  />
                  <v-checkbox
                    v-if="user.id"
                    id="is-deleted"
                    v-model="user.deletedAt"
                    density="compact"
                    color="primary"
                    label="Deleted"
                    :value="Date()"
                    :hide-details="true"
                  />
                </div>
                <div>
                  <v-checkbox
                    id="can-access-canvas-data"
                    v-model="user.canAccessCanvasData"
                    density="compact"
                    color="primary"
                    label="Canvas Data"
                    :hide-details="true"
                  />
                  <v-checkbox
                    id="can-access-advising-data"
                    v-model="user.canAccessAdvisingData"
                    density="compact"
                    color="primary"
                    label="Notes and Appointments"
                    :hide-details="true"
                  />
                </div>
              </div>
            </div>
            <div v-if="isCoe(user) || user.degreeProgressPermission">
              <label class="font-weight-black" for="degree-progress-permission-select">Degree Progress Permission</label>
              <div class="mt-1">
                <select
                  id="degree-progress-permission-select"
                  v-model="user.degreeProgressPermission"
                  class="select-menu w-50"
                >
                  <option id="department-null" :value="null">Select...</option>
                  <option
                    v-for="option in [{value: 'read', text: 'Read-only'}, {value: 'read_write', text: 'Read and write'}]"
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
                  v-model="user.automateDegreeProgressPermission"
                  density="compact"
                  color="primary"
                  label="Automate Degree Progress permissions"
                  :hide-details="true"
                />
              </div>
            </div>
            <h4 class="sr-only">Departments</h4>
            <v-card
              v-for="department in user.departments"
              :key="department.deptCode"
              class="bg-grey-lighten-4 border-md mt-1"
              flat
            >
              <v-card-title class="align-center d-flex">
                <h5 class="text-wrap font-size-16">{{ department.deptName }} ({{ department.deptCode }})</h5>
                <div v-for="d in user.departments" :key="d.id">
                  <v-btn
                    v-for="membership in d.memberships"
                    :id="`remove-department-${d.deptCode}`"
                    :key="membership.role"
                    :aria-label="`Remove department '${d.deptName}'`"
                    class="align-self-start bg-grey-lighten-4 ml-auto text-error"
                    density="comfortable"
                    :icon="mdiCloseCircleOutline"
                    title="Remove"
                    variant="flat"
                    @click="() => removeDepartment(d.deptCode, membership.role)"
                  />
                </div>
              </v-card-title>
              <v-card-text class="pl-4">
                <div class="align-center d-flex">
                  <label class="font-weight-black mr-2" :for="`select-department-${department.deptCode}-role`">Role</label>
                  <select
                    :id="`select-department-${department.deptCode}-role`"
                    v-model="role"
                    class="select-menu select-department-role"
                    :class="{'border border-error border-opacity-100 text-error': includes(map(membershipsMissingRoles, 'deptCode'), department.deptCode)}"
                    @change="remove(membershipsMissingRoles, ['deptCode', department.deptCode])"
                  >
                    <option
                      id="department-role-null"
                      :value="undefined"
                    >
                      Select...
                    </option>
                    <option
                      v-for="option in [
                        {value: 'advisor', text: 'Advisor'},
                        {value: 'director', text: 'Director'},
                        {value: 'peer_advisor_manager', text: 'Peer Advisor Manager'}
                      ]"
                      :id="`department-role-${lowerCase(option.value)}`"
                      :key="option.value"
                      :disabled="isRoleOptionDisabled(department.deptCode, option.value)"
                      :value="option.value"
                    >
                      {{ option.text }}
                    </option>
                  </select>
                </div>
                <div v-for="membership in department.memberships" :key="membership.role">
                  <v-expand-transition>
                    <div v-show="membership.role !== 'peer_advisor_manager'" class="pl-8 pt-1">
                      <v-checkbox
                        :id="`is-automate-membership-${department.deptCode}`"
                        v-model="membership.automateMembership"
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
                  <v-expand-transition>
                    <div v-show="membership.role === 'peer_advisor_manager'" class="mt-2 pl-11 pr-8">
                      <select
                        id="peer-advising-department-select"
                        v-model="membership.peerAdvisingDepartmentId"
                        aria-label="Department"
                        class="select-menu w-100"
                        @change="addDepartment"
                      >
                        <option id="department-null" :value="undefined">
                          Select Peer Advising Department...
                        </option>
                        <option
                          v-for="option in getPeerAdvisingDepartments(department.deptCode)"
                          :id="`department-option-${lowerCase(toString(option.id))}`"
                          :key="option.id"
                          :disabled="isDepartmentOptionDisabled(option.id)"
                          :value="option.id"
                        >
                          {{ option.name }}
                        </option>
                      </select>
                    </div>
                  </v-expand-transition>
                </div>
              </v-card-text>
            </v-card>
            <div v-if="user.departments.length >= 3">
              <span class="text-info"><v-icon class="mb-1" :icon="mdiCheckBold" /> Three departments is enough!</span>
            </div>
            <div v-if="user.departments.length < 3" class="pt-2">
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
                  v-for="berkeleyDepartment in allBerkeleyDepartments"
                  :id="`department-option-${lowerCase(berkeleyDepartment.deptCode)}`"
                  :key="berkeleyDepartment.deptCode"
                  :disabled="isDepartmentOptionDisabled(berkeleyDepartment.deptCode)"
                  :value="berkeleyDepartment.deptCode"
                >
                  {{ berkeleyDepartment.deptName }}
                </option>
              </select>
            </div>
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
        </FocusLock>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import FocusLock from 'vue-focus-lock'
import ModalHeader from '@/components/util/ModalHeader.vue'
import ProgressButton from '@/components/util/ProgressButton.vue'
import {
  BoaUser,
  Department,
  DepartmentMembershipRole,
  PeerAdvisingDepartment,
  alertScreenReader,
  putFocusNextTick,
  scrollTo
} from '@/lib/utils'
import {PropType, ref} from 'vue'
import {createOrUpdateUser} from '@/api/user'
import {filter as _filter, find, get, includes, lowerCase, map, remove, size, toString} from 'lodash'
import {isCoe} from '@/berkeley'
import {mdiAlert, mdiCheckBold, mdiCloseCircleOutline, mdiNoteEditOutline, mdiPlus} from '@mdi/js'

const props = defineProps({
  afterSave: {
    default: () => {},
    type: Function
  },
  allBerkeleyDepartments: {
    required: true,
    type: Array as PropType<Array<Department>>
  }
})

const user = defineModel<BoaUser>({
  required: true,
  type: Object as PropType<BoaUser>
})

const deptCode = ref(undefined)
const disabledDepartmentOptions = ref<string[]>([])
const errors = ref<string[]>([])
const isSaving = ref(false)
const membershipsMissingRoles = ref([])
const role = ref(undefined)
const showEditUserModal = ref(false)

const addDepartment = () => {
  if (deptCode.value) {
    const department = find(props.allBerkeleyDepartments.value, ['deptCode', deptCode.value])
    if (department) {
      user.value.departments.push({
        ...department,
        ...{memberships: []}
      })
      disabledDepartmentOptions.value.push(department.deptCode)
    }
  }
}

const cancel = () => {
  closeModal()
  alertScreenReader('Canceled')
  if (user.value.id) {
    alertScreenReader('Canceled')
    putFocusNextTick(`edit-${user.value.uid}`)
  } else {
    putFocusNextTick('add-new-user-btn')
  }
}

const clearErrors = () => {
  errors.value = []
  membershipsMissingRoles.value = []
}

const closeModal = () => {
  clearErrors()
  showEditUserModal.value = false
}

const getPeerAdvisingDepartments = (deptCode: string): PeerAdvisingDepartment[] | undefined => {
  const department = find(props.allBerkeleyDepartments.value, ['deptCode', deptCode])
  return department && department.peerAdvisingDepartments
}

const isDepartmentOptionDisabled = deptCode => {
  return !deptCode
  // TODO:
  // const existing_roles = map(_filter(user.value.departments, ['deptCode', deptCode]), 'role')
  // return existing_roles.length === 2 && existing_roles.includes('peer_advisor_manager')
}

const isRoleOptionDisabled = (deptCode, role) => {
  let isDisabled = false
  const memberships_per_dept_code = _filter(user.value.departments, ['deptCode', deptCode])
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
  showEditUserModal.value = true
  putFocusNextTick(user.value.uid ? 'is-admin' : 'uid-input')
}

const removeDepartment = (deptCode: string, role: DepartmentMembershipRole) => {
  const department = find(user.value.departments, ['deptCode', deptCode])
  if (department) {
    const indexOf = department.memberships.findIndex(m => m.role === role)
    department.memberships.splice(indexOf, 1)
    // TODO:
    // const option = find(allBerkeleyDepartments.value, ['value', deptCode])
    // option.disabled = false
  }
}

const save = () => {
  clearErrors()
  if (!user.value.uid) {
    errors.value.push('UID is required')
  }
  if (!membershipsMissingRoles.value.length) {
    isSaving.value = true
    // If no change in deleted status then do not update 'deleted_at' in the database.
    // const deleteAction = isDeleted.value === !!props.profile.deletedAt ? null : isDeleted.value
    createOrUpdateUser(user.value).then(() => {
      props.afterSave(user.value)
      closeModal()
    }).catch(error => {
      errors.value.push(get(error, 'response.data.message', error))
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
  background-color: rgb(var('--v-theme-surface'));
  min-width: 120px;
  z-index: 1;
}
</style>

<style>
.automate-membership-checkbox .v-label {
  opacity: var('--v-high-emphasis-opacity') !important;
}
</style>
