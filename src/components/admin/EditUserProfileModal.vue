<template>
  <div>
    <b-btn
      v-if="isExistingUser"
      :id="`edit-${profile.uid}`"
      :title="`Edit profile of ${profile.name}`"
      class="pl-1 pr-1"
      variant="link"
      @click="openEditUserModal">
      <font-awesome icon="edit" />
    </b-btn>
    <b-btn
      v-if="!isExistingUser"
      id="add-new-user-btn"
      class="pl-1 pr-1"
      variant="link"
      @click="openEditUserModal">
      <div class="d-flex">
        <div class="pr-1">
          <font-awesome icon="plus" />
        </div>
        <div>
          Add New User
        </div>
      </div>
    </b-btn>
    <b-modal
      v-if="showEditUserModal"
      v-model="showEditUserModal"
      body-class="pl-0 pr-0"
      hide-footer
      hide-header
      @shown="focusModalById('edit-modal-header')">
      <div class="modal-header">
        <h2 id="edit-modal-header" class="student-section-header">{{ isExistingUser ? profile.name : 'Create User' }}</h2>
      </div>
      <div class="modal-body m-0 p-0">
        <div class="pt-2">
          <div
            v-if="error"
            class="align-items-center has-error mb-3 ml-4 mt-1"
            aria-live="polite"
            role="alert">
            <span class="font-weight-bolder">Error:</span> {{ error }}
          </div>
          <div v-if="!isExistingUser" class="align-items-center mb-3 ml-4 mt-3">
            <label for="uid-input" class="sr-only">U I D</label>
            <b-form-input
              id="uid-input"
              v-model="userProfile.uid"
              class="w-260px"
              maxlength="10"
              placeholder="UID"
              size="lg"></b-form-input>
          </div>
          <b-container fluid class="ml-2">
            <b-row>
              <b-col><label for="is-admin">Admin</label></b-col>
              <b-col><b-form-checkbox id="is-admin" v-model="userProfile.isAdmin"></b-form-checkbox></b-col>
            </b-row>
            <b-row>
              <b-col><label for="is-blocked">Blocked</label></b-col>
              <b-col><b-form-checkbox id="is-blocked" v-model="userProfile.isBlocked"></b-form-checkbox></b-col>
            </b-row>
            <b-row>
              <b-col><label for="can-access-canvas-data">Canvas Data</label></b-col>
              <b-col><b-form-checkbox id="can-access-canvas-data" v-model="userProfile.canAccessCanvasData"></b-form-checkbox></b-col>
            </b-row>
            <b-row>
              <b-col><label for="can-access-advising-data">Notes and Appointments</label></b-col>
              <b-col><b-form-checkbox id="can-access-advising-data" v-model="userProfile.canAccessAdvisingData"></b-form-checkbox></b-col>
            </b-row>
            <b-row v-if="profile.id">
              <b-col><label for="is-deleted">Deleted</label></b-col>
              <b-col><b-form-checkbox id="is-deleted" v-model="isDeleted"></b-form-checkbox></b-col>
            </b-row>
          </b-container>
        </div>
        <hr class="mb-1 ml-0 mr-0 mt-1" />
        <div class="ml-3 mr-2 pt-2">
          <h3 class="color-grey font-size-18 mb-1">Departments</h3>
          <div
            v-for="dept in memberships"
            :key="dept.code"
            class="ml-2 mt-2">
            <div class="align-items-center d-flex">
              <div>
                <h4 class="font-size-16">
                  {{ dept.name }} ({{ dept.code }})
                </h4>
              </div>
              <div class="mb-1">
                <b-btn
                  :id="`remove-department-${dept.code}`"
                  variant="link"
                  class="p-0"
                  @click.prevent="removeDepartment(dept.code)">
                  <font-awesome icon="times-circle" class="font-size-24 has-error pl-2" />
                  <span class="sr-only">Remove department '{{ dept.name }}'</span>
                </b-btn>
              </div>
            </div>
            <div class="pl-4">
              <div class="align-items-center d-flex">
                <div class="font-weight-500 pr-2 pt-1">
                  <label :for="`select-department-${dept.code}-role`">Role:</label>
                </div>
                <b-form-select
                  :id="`select-department-${dept.code}-role`"
                  v-model="dept.role"
                  :options="[
                    {text: 'Advisor', value: 'advisor'},
                    {text: 'Director', value: 'director'},
                    {text: 'Scheduler', value: 'scheduler'}
                  ]"
                  :aria-label="`User's role in department ${dept.name}`"
                  class="w-260px">
                  <template v-slot:first>
                    <option :value="undefined">Select...</option>
                  </template>
                </b-form-select>
              </div>
              <div class="d-flex pt-2">
                <div class="font-weight-500">
                  <label :for="`is-automated-membership-${dept.code}`">Automated</label>
                </div>
                <div class="pl-1">
                  <b-form-checkbox :id="`is-automate-membership-${dept.code}`" v-model="dept.automateMembership"></b-form-checkbox>
                </div>
              </div>
            </div>
          </div>
          <div v-if="memberships.length >= 3" class="m-3">
            <span class="text-info"><font-awesome icon="check" /> Three departments is enough!</span>
          </div>
          <div v-if="memberships.length < 3" class="mb-3 ml-0 mr-2 p-2">
            <b-form-select
              id="department-select-list"
              v-model="deptCode"
              :options="departmentOptions"
              class="w-auto"
              aria-label="Use up and down arrows to review departments. Hit enter to select a department."
              @change="addDepartment">
              <template v-slot:first>
                <option :value="undefined">Add department...</option>
              </template>
            </b-form-select>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <b-btn
          id="save-changes-to-user-profile"
          class="btn-primary-color-override"
          variant="primary"
          @click="save">
          Save
        </b-btn>
        <b-btn
          id="delete-cancel"
          class="pl-2"
          variant="link"
          @click="cancel"
          @keyup.enter="cancel">
          Cancel
        </b-btn>
      </div>
    </b-modal>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import { createOrUpdateUser } from '@/api/user'

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
    memberships: undefined,
    showEditUserModal: false,
    userProfile: undefined
  }),
  computed: {
    isExistingUser() {
      return !!this.profile.id
    }
  },
  methods: {
    addDepartment() {
      if (this.deptCode) {
        const dept = this.$_.find(this.departments, ['code', this.deptCode])
        this.memberships.push({
          code: dept.code,
          name: dept.name,
          role: undefined,
          automateMembership: true
        })
        const option = this.$_.find(this.departmentOptions, ['value', this.deptCode])
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
    openEditUserModal() {
      this.putFocusNextTick(this.profile.id ? 'edit-modal-header' : 'uid-input')
      this.userProfile = {
        id: this.profile.id,
        uid: this.profile.uid,
        name: this.profile.name,
        canAccessAdvisingData: this.profile.canAccessAdvisingData,
        canAccessCanvasData: this.profile.canAccessCanvasData,
        departments: [],
        isAdmin: this.profile.isAdmin,
        isBlocked: this.profile.isBlocked
      }
      this.isDeleted = !!this.profile.deletedAt
      this.memberships = []
      this.$_.each(this.profile.departments, d => {
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
      this.$_.each(this.departments, d => {
        this.departmentOptions.push({
          disabled: !!this.$_.find(this.memberships, ['code', d.code]),
          value: d.code,
          text: d.name
        })
      })
      this.showEditUserModal = true
    },
    removeDepartment(deptCode) {
      let indexOf = this.memberships.findIndex(d => d.code === deptCode)
      this.memberships.splice(indexOf, 1)
      const option = this.$_.find(this.departmentOptions, ['value', deptCode])
      option.disabled = false
    },
    save() {
      const undefinedRoles = this.$_.filter(this.memberships, r => this.isNil(r.role))
      if (undefinedRoles.length) {
        const deptNames = this.map(undefinedRoles, 'name')
        this.error = `Please specify role for ${this.oxfordJoin(deptNames)}`
      } else {
        // If no change in deleted status then do not update 'deleted_at' in the database.
        const deleteAction = this.isDeleted === !!this.profile.deletedAt ? null : this.isDeleted
        createOrUpdateUser(this.userProfile, this.memberships, deleteAction).then(() => {
          this.afterUpdateUser(this.profile)
          this.closeModal()
        }).catch(error => {
          this.error = this.$_.get(error, 'response.data.message') || error
        })
      }
    }
  }
}
</script>

<style scoped>
.w-260px {
  width: 260px;
}
</style>
