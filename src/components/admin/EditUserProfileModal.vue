<template>
  <div>
    <v-icon
      v-if="isExistingUser"
      :id="`edit-${profile.uid}`"
      class="pl-1 pr-1 cursor-pointer"
      :icon="mdiNoteEditOutline"
      size="x-large"
      @click="openEditUserModal"
    >
      <span class="sr-only"> Edit profile of {{ profile.name }}</span>
    </v-icon>
    <v-btn
      v-if="!isExistingUser"
      id="add-new-user-btn"
      class="pl-4 pr-4 mr-6"
      color="primary"
      :prepend-icon="mdiPlus"
      @click="openEditUserModal"
    >
      <div class="d-flex">
        <div>
          Add New User
        </div>
      </div>
    </v-btn>

    <v-dialog
      v-model="showEditUserModal"
      width="auto"
    >
      <v-card
        min-width="600"
        max-width="600"
      >
        <v-card-text>
          <h2 v-if="!isExistingUser">Create User</h2>
          <h2 v-if="isExistingUser">{{ profile.name }}</h2>
          <div class="modal-body m-0 p-0">
            <div>
              <div
                v-if="error"
                class="align-items-center has-error mb-3 ml-4 mt-1"
                aria-live="polite"
                role="alert"
              >
                <span class="font-weight-bolder text-red">Error: {{ error }}</span>
              </div>
              <div v-if="!isExistingUser" class="align-items-center ml-0 mt-3">
                <label for="uid-input" class="sr-only">U I D </label>
                <v-text-field
                  v-model="userProfile.uid"
                  label="UID"
                  variant="outlined"
                  density="compact"
                >
                </v-text-field>
              </div>
              <div class="ml-0 mt-0">
                <v-checkbox
                  id="is-admin"
                  v-model="userProfile.isAdmin"
                  label="Admin"
                  hide-details="true"
                >
                </v-checkbox>
                <v-checkbox
                  id="is-blocked"
                  v-model="userProfile.isBlocked"
                  label="Blocked"
                  hide-details="true"
                >
                </v-checkbox>
                <v-checkbox
                  id="can-access-canvas-data"
                  v-model="userProfile.canAccessCanvasData"
                  label="Canvas Data"
                  hide-details="true"
                >
                </v-checkbox>
                <v-checkbox
                  id="can-access-advising-data"
                  v-model="userProfile.canAccessAdvisingData"
                  label="Notes and Appointments"
                  hide-details="true"
                >
                </v-checkbox>
                <v-checkbox
                  v-if="profile.id"
                  id="is-deleted"
                  v-model="isDeleted"
                  label="Deleted"
                  hide-details="true"
                >
                </v-checkbox>
                <v-row v-if="isCoe({departments: memberships}) || userProfile.degreeProgressPermission">
                  <v-col class="mr-3" no-gutters>
                    <!-- <label for="degree-progress-permission">Degree Progress Permission</label> -->
                    <div class="mt-1 ">
                      <v-select
                        v-model="userProfile.degreeProgressPermission"
                        label="Degree Progress Permission"
                        :items="degreeProgressPermissionItems"
                        item-title="text"
                        item-value="value"
                        density="compact"
                        variant="outlined"
                      ></v-select>
                      <!-- <b-select
                        id="degree-progress-permission-select"
                        v-model="userProfile.degreeProgressPermission"
                        :options="[
                          {value: null, text: 'Select...'},
                          {value: 'read', text: 'Read-only'},
                          {value: 'read_write', text: 'Read and write'}
                        ]"
                      /> -->
                      <div class="d-flex pl-1 pt-2">
                        <div class="pl-1">
                          <v-checkbox
                            id="automate-degree-progress-permission"
                            v-model="userProfile.automateDegreeProgressPermission"
                            label="Automate Degree Progress permissions"
                            hide-details="true"
                          >
                          </v-checkbox>
                        </div>
                      </div>
                    </div>
                  </v-col>
                </v-row>
              </div>
            </div>
            <hr class="mb-1 ml-0 mr-0 mt-1" />
            <div class="ml-3 mr-2 pt-2">
              <h3 class="color-grey font-size-18 mb-1">Departments</h3>
              <div
                v-for="dept in memberships"
                :key="dept.code"
                class="ml-0 mt-2"
              >
                <div class="align-items-center d-flex">
                  <div>
                    <h4 class="font-size-16">
                      {{ dept.name }} ({{ dept.code }})
                    </h4>
                  </div>
                  <div class="mb-1">
                    <v-icon
                      :id="`remove-department-${dept.code}`"
                      :icon="mdiCloseCircleOutline"
                      class="pl-2 pb-1"
                      size="x-large"
                      color="error"
                      @click.prevent="removeDepartment(dept.code)"
                    >
                      <span class="sr-only">Remove department '{{ dept.name }}'</span>
                    </v-icon>
                  </div>
                </div>
                <div class="pl-4">
                  <div class="align-items-center d-flex">
                    <!-- <div class="font-weight-500 pr-2 pt-1">
                      <label :for="`select-department-${dept.code}-role`">Role:</label>
                    </div> -->
                    <v-select
                      :id="`select-department-${dept.code}-role`"
                      v-model="dept.role"
                      class="w-260px"
                      label="Role: "
                      :items="departmentItems"
                      item-title="text"
                      item-value="value"
                      density="compact"
                      variant="outlined"
                    >
                    </v-select>
                    <!-- <select
                      :id="`select-department-${dept.code}-role`"
                      v-model="dept.role"
                      :aria-label="`User's role in department ${dept.name}`"
                      class="w-260px"
                      style="font-size: 16px;"
                    >
                      <option :value="undefined">Select...</option>
                      <option value="advisor">Advisor</option>
                      <option value="director">Director</option>
                    </select> -->
                  </div>
                  <div class="d-flex">
                    <!-- <div class="font-weight-500">
                      <label :for="`is-automated-membership-${dept.code}`">Automated</label>
                    </div> -->
                    <div class="mb-1">
                      <!-- <b-form-checkbox :id="`is-automate-membership-${dept.code}`" v-model="dept.automateMembership"></b-form-checkbox> -->
                      <v-checkbox
                        :id="`is-automate-membership-${dept.code}`"
                        v-model="dept.automateMembership"
                        label="Automated"
                        hide-details="true"
                      >
                      </v-checkbox>
                    </div>
                  </div>
                </div>
              </div>
              <div v-if="memberships.length >= 3" class="m-3">
                <span class="text-info"><v-icon class="mb-1" :icon="mdiCheckBold" /> Three departments is enough!</span>
              </div>

              <div v-if="memberships.length < 3" class="ml-0 mr-2 p-2 mt-4">
                <v-row no-gutters>
                  <v-col cols="12" md="10">
                    <v-select
                      id="department-select-list"
                      v-model="deptCode"
                      label="Add Department"
                      :items="departmentOptions"
                      item-title="text"
                      item-value="value"
                      density="compact"
                      variant="outlined"
                    >
                    </v-select>
                  </v-col>

                  <v-col cols="12" md="2">
                    <v-btn
                      id="add-department-button"
                      class="ml-2 pb-1"
                      icon
                      variant="text"
                      @click="addDepartment"
                    >
                      <v-icon :icon="mdiPlus"></v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </div>
            </div>
          </div>
        </v-card-text>
        <template #actions>
          <v-btn
            color="primary"
            variant="flat"
            :disabled="isSaving"
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
            text="Cancel"
            color="primary"
            variant="text"
            @click="cancel"
          ></v-btn>
        </template>
      </v-card>
    </v-dialog>



    <!-- <v-modal
      v-if="showEditUserModal"
      v-model="showEditUserModal"
      body-class="pl-0 pr-0"
      hide-footer
      hide-header
      @shown="putFocusNextTick('modal-header')"
    >
      <ModalHeader :text="isExistingUser ? profile.name : 'Create User'" />

      <div class="modal-footer">
        <v-btn
          id="save-changes-to-user-profile"
          class="btn-primary-color-override"
          :disabled="isSaving"
          variant="primary"
          @click="save"
        >
          <span v-if="isSaving"><font-awesome class="mr-1" icon="spinner" spin /> Saving</span>
          <span v-if="!isSaving">Save</span>
        </v-btn>
        <v-btn
          id="delete-cancel"
          class="pl-2"
          :disabled="isSaving"
          variant="link"
          @click="cancel"
          @keyup.enter="cancel"
        >
          Cancel
        </v-btn>
      </div>
    </v-modal> -->
  </div>
</template>

<script setup>
import {mdiNoteEditOutline} from '@mdi/js'
import {mdiPlus} from '@mdi/js'
import {mdiCloseCircleOutline} from '@mdi/js'
import {mdiCheckBold} from '@mdi/js'

</script>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import {createOrUpdateUser} from '@/api/user'
import {isCoe} from '@/berkeley'

export default {
  name: 'EditUserProfileModal',
  mixins: [Context, Util],
  props: {
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
    memberships: undefined,
    showEditUserModal: false,
    userProfile: undefined,
    degreeProgressPermissionItems: [
      {value: null, text: 'Select...'},
      {value: 'read', text: 'Read-only'},
      {value: 'read_write', text: 'Read and write'}
    ],
    departmentItems: [
      {value: null, text: 'Select...'},
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
        const dept = this._find(this.departments, ['code', this.deptCode])
        this.memberships.push({
          code: dept.code,
          name: dept.name,
          role: undefined,
          automateMembership: true
        })
        const option = this._find(this.departmentOptions, ['value', this.deptCode])
        option.disabled = true
        this.deptCode = undefined
      }
    },
    cancel() {
      this.closeModal()
    },
    closeModal() {
      this.error = undefined
      this.userProfile = undefined
      this.memberships = undefined
      this.showEditUserModal = false
    },
    isCoe,
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

<style scoped>
.w-260px {
  width: 260px;
  max-width: 260px;
}

.max-width{
  width: 300px;
  max-width: 300px;
}

:deep(.v-input__details) {
  min-height: 0px !important;
  max-height: 6px !important;
}

/* Scoped styles for checkbox */
.v-input--density-default {
  --v-input-control-height: 0 !important;
}

.v-input--checkbox .v-input--selection-controls__input {
  margin: 0;
}
</style>
