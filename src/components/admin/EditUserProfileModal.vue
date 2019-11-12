<template>
  <div>
    <b-btn
      :id="'edit-${user.uid}'"
      :title="`Edit profile of ${profile.name}`"
      @click="openEditUserModal()"
      class="pl-1 pr-1"
      variant="link">
      <font-awesome icon="edit" />
    </b-btn>
    <b-modal
      v-if="showEditUserModal"
      v-model="showEditUserModal"
      @shown="focusModalById('edit-modal-header')"
      body-class="pl-0 pr-0"
      hide-footer
      hide-header>
      <div class="modal-header">
        <h2 id="edit-modal-header" class="student-section-header">{{ profile.name }}</h2>
      </div>
      <div class="modal-body m-0 p-0">
        <div class="pt-2">
          <b-container fluid class="ml-2 w-50">
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
          </b-container>
        </div>
        <hr class="mb-1 ml-0 mr-0 mt-1" />
        <div class="ml-3 mr-2 pt-2">
          <h3 class="color-grey font-size-18 mb-1">Departments</h3>
          <div
            v-for="dept in userProfile.departments"
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
                  @click.prevent="removeDepartment(dept.code)"
                  variant="link"
                  class="p-0">
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
                  :options="[
                    { text: 'Advisor', value: 'advisor' },
                    { text: 'Advisor + Drop-In', value: 'dropInAdvisor' },
                    { text: 'Director', value: 'director' },
                    { text: 'Scheduler', value: 'scheduler' },
                  ]"
                  v-model="dept.role"
                  :aria-label="`User's role in department ${dept.name}`"
                  class="w-200px">
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
          <div v-if="userProfile.departments.length >= 3" class="m-3">
            <span class="text-info"><font-awesome icon="check" /> Three departments is enough!</span>
          </div>
          <div v-if="userProfile.departments.length < 3" class="mb-3 ml-0 mr-2 p-2">
            <b-form-select
              id="department-select-list"
              v-model="deptCode"
              :options="departmentOptions"
              @change="addDepartment"
              aria-label="Use up and down arrows to review departments. Hit enter to select a department.">
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
          @click="save()"
          class="btn-primary-color-override"
          variant="primary">
          Save
        </b-btn>
        <b-btn
          id="delete-cancel"
          @click="cancel()"
          @keyup.enter="cancel()"
          class="pl-2"
          variant="link">
          Cancel
        </b-btn>
      </div>
    </b-modal>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'EditUserProfileModal',
  mixins: [Context, UserMetadata, Util],
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
      required: true,
      type: Object
    }
  },
  data: () => ({
    departmentOptions: undefined,
    deptCode: undefined,
    showEditUserModal: false,
    userProfile: undefined
  }),
  methods: {
    addDepartment() {
      if (this.deptCode) {
        const dept = this.find(this.departments, ['code', this.deptCode]);
        this.userProfile.departments.push({
          code: dept.code,
          name: dept.name,
          role: undefined,
          automateMembership: true
        });
        const option = this.find(this.departmentOptions, ['value', this.deptCode]);
        option.disabled = true;
        this.deptCode = undefined;
      }
    },
    cancel() {
      this.showEditUserModal = false;
    },
    openEditUserModal() {
      this.userProfile = this.cloneDeep(this.profile);
      this.each(this.userProfile.departments, d => {
        if (this.find(this.userProfile.dropInAdvisorStatus, ['deptCode', d.code])) {
          d.role = 'dropInAdvisor';
        } else if (d.isAdvisor) {
          d.role = 'advisor';
        } else if (d.isDirector) {
          d.role = 'director';
        } else if (d.isScheduler) {
          d.role = 'scheduler';
        }
      });
      this.departmentOptions = [];
      this.each(this.departments, d => {
        this.departmentOptions.push({
          disabled: !!this.find(this.userProfile.departments, ['code', d.code]),
          value: d.code,
          text: d.name
        });
      });
      this.showEditUserModal = true;
    },
    removeDepartment(deptCode) {
      let indexOf = this.userProfile.departments.findIndex(d => d.code === deptCode);
      this.userProfile.departments.splice(indexOf, 1);
      const option = this.find(this.departmentOptions, ['value', deptCode]);
      option.disabled = false;
    },
    save() {
      this.showEditUserModal = false;
      this.afterUpdateUser();
    }
  }
};
</script>

<style scoped>
.w-100px {
  width: 100px;
}
.w-200px {
  width: 200px;
}
</style>
