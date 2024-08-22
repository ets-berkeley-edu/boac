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
      <FocusLock>
        <v-card
          class="modal-content"
          max-width="600"
          min-width="600"
        >
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
                >
                </v-btn>
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
            <div v-if="memberships.length < 3" class="mt-2 w-100">
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
            <v-btn
              id="save-changes-to-user-profile"
              color="primary"
              :disabled="isSaving || !userProfile.uid || memberships.findIndex(d => !d.role) >= 0"
              variant="flat"
              @click="save"
            >
              <span v-if="!isSaving">Save</span>
              <v-progress-circular
                v-if="isSaving"
                indeterminate
                :size="18"
                :width="4"
              />
            </v-btn>
            <v-btn
              id="cancel-changes-to-user-profile"
              class="ml-2"
              text="Cancel"
              variant="text"
              @click="cancel"
            />
          </v-card-actions>
        </v-card>
      </FocusLock>
    </v-dialog>
  </div>
</template>

<script setup>
import ModalHeader from '@/components/util/ModalHeader'
import {lowerCase} from 'lodash'
import {mdiNoteEditOutline} from '@mdi/js'
import {mdiPlus} from '@mdi/js'
import {mdiCloseCircleOutline} from '@mdi/js'
import {mdiCheckBold} from '@mdi/js'
import {putFocusNextTick} from '@/lib/utils'
</script>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import {createOrUpdateUser} from '@/api/user'
import {isCoe} from '@/berkeley'
import {find} from 'lodash'

export default {
  name: 'EditUserProfileModal',
  mixins: [Context, Util],
  props: {
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
  },
  data: () => ({
    departmentOptions: undefined,
    deptCode: undefined,
    error: undefined,
    isDeleted: undefined,
    isSaving: false,
    memberships: [],
    showEditUserModal: false,
    userProfile: {},
    degreeProgressPermissionItems: [
      {value: 'read', text: 'Read-only'},
      {value: 'read_write', text: 'Read and write'}
    ],
    roles: [
      {value: 'advisor', text: 'Advisor'},
      {value: 'director', text: 'Director'}
    ]
  }),
  computed: {
    isExistingUser() {
      return !!this.profile.id
    }
  },
  methods: {
    addDepartment() {
      if (this.deptCode) {
        const dept = find(this.departments, ['code', this.deptCode])
        this.memberships.push({
          code: dept.code,
          name: dept.name,
          role: null,
          automateMembership: true
        })
        const option = find(this.departmentOptions, ['value', this.deptCode])
        option.disabled = true
        this.deptCode = undefined
      }
    },
    cancel() {
      this.closeModal()
      this.afterCancel(this.profile)
    },
    closeModal() {
      this.showEditUserModal = false
      this.error = undefined
      this.userProfile = {}
      this.memberships = []
    },
    openEditUserModal() {
      this.userProfile = {
        id: this.profile.id,
        uid: this.profile.uid,
        name: this.profile.name,
        automateDegreeProgressPermission: this.profile.automateDegreeProgressPermission || false,
        canAccessAdvisingData: this.profile.canAccessAdvisingData,
        canAccessCanvasData: this.profile.canAccessCanvasData,
        degreeProgressPermission: this.profile.degreeProgressPermission || null,
        departments: [],
        isAdmin: this.profile.isAdmin,
        isBlocked: this.profile.isBlocked
      }
      this.isDeleted = !!this.profile.deletedAt
      this.memberships = []
      this._each(this.profile.departments, d => {
        if (d.role) {
          this.memberships.push({
            automateMembership: d.automateMembership,
            code: d.code,
            name: d.name,
            role: d.role,
          })
        }
      })
      this.departmentOptions = []
      this._each(this.departments, d => {
        this.departmentOptions.push({
          disabled: !!this._find(this.memberships, ['code', d.code]),
          value: d.code,
          text: d.name
        })
      })
      this.showEditUserModal = true
      putFocusNextTick(this.profile.uid ? 'is-admin' : 'uid-input')
    },
    removeDepartment(deptCode) {
      let indexOf = this.memberships.findIndex(d => d.code === deptCode)
      this.memberships.splice(indexOf, 1)
      const option = this._find(this.departmentOptions, ['value', deptCode])
      option.disabled = false
    },
    save() {
      const undefinedRoles = this._filter(this.memberships, r => this._isNil(r.role))
      if (undefinedRoles.length) {
        const deptNames = this._map(undefinedRoles, 'name')
        this.error = `Please specify role for ${this.oxfordJoin(deptNames)}`
      } else {
        this.isSaving = true
        // If no change in deleted status then do not update 'deleted_at' in the database.
        const deleteAction = this.isDeleted === !!this.profile.deletedAt ? null : this.isDeleted
        createOrUpdateUser(this.userProfile, this.memberships, deleteAction).then(() => {
          this.afterUpdateUser(this.profile)
          this.closeModal()
        }).catch(error => {
          this.error = this._get(error, 'response.data.message') || error
        }).finally(() => {
          this.isSaving = false
        })
      }
    }
  }
}
</script>
