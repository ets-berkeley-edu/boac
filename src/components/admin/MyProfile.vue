<template>
  <b-container class="m-3 pr-5" fluid>
    <EditMyRolesModal
      v-if="showEditRolesModal"
      :after-save="afterSaveRoles"
      :cancel="cancelEditRoles"
      :dept-code="editingRolesForDeptCode"
      :show-modal="showEditRolesModal" />
    <b-row align-v="start" class="border-bottom border-top p-2">
      <b-col class="font-weight-500" cols="3">
        Name
      </b-col>
      <b-col>
        {{ $currentUser.name }}
      </b-col>
    </b-row>
    <b-row align-v="start" class="border-bottom p-2">
      <b-col class="font-weight-500" cols="3">
        UID
      </b-col>
      <b-col>
        {{ $currentUser.uid }}
      </b-col>
    </b-row>
    <b-row align-v="start" class="border-bottom p-2">
      <b-col class="font-weight-500" cols="3">
        Campus Solutions ID
      </b-col>
      <b-col>
        {{ $currentUser.csid }}
      </b-col>
    </b-row>
    <b-row align-v="start" class="border-bottom p-2">
      <b-col class="font-weight-500" cols="3">
        Email
      </b-col>
      <b-col>
        {{ $currentUser.email }}
      </b-col>
    </b-row>
    <b-row align-v="start" class="border-bottom p-2">
      <b-col class="font-weight-500 v-align-middle" cols="3">
        Roles
      </b-col>
      <b-col>
        <div v-if="$currentUser.isAdmin || !$currentUser.canAccessCanvasData">
          <span v-if="$currentUser.isAdmin">You are a BOA Admin user.</span>
          <span v-if="!$currentUser.canAccessCanvasData">You do not have access to bCourses (LMS) data.</span>
        </div>
        <div v-if="$currentUser.departments.length">
          <div v-for="department in $currentUser.departments" :key="department.code">
            <span id="my-dept-roles">{{ oxfordJoin(getRoles(department)) }} in {{ department.name }}.</span>
            <b-btn
              v-if="includes(dropInAdvisorDeptCodes, department.code)"
              id="btn-edit-my-dept-roles"
              variant="link"
              class="mb-1"
              aria-label="Edit roles. Modal window will open."
              @click="openEditRolesModal(department.code)">
              edit
            </b-btn>
          </div>
        </div>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import Berkeley from '@/mixins/Berkeley';
import Context from '@/mixins/Context';
import EditMyRolesModal from '@/components/admin/EditMyRolesModal';
import Util from '@/mixins/Util';

export default {
  name: 'MyProfile',
  components: {EditMyRolesModal},
  mixins: [Berkeley, Context, Util],
  data: () => ({
    dropInAdvisorDeptCodes: undefined,
    editingRolesForDeptCode: undefined,
    showEditRolesModal: false
  }),
  created() {
    this.dropInAdvisorDeptCodes = this.map(this.$currentUser.dropInAdvisorStatus, 'deptCode');
  },
  methods: {
    afterSaveRoles() {
      this.showEditRolesModal = false;
      this.dropInAdvisorDeptCodes = this.map(this.$currentUser.dropInAdvisorStatus, 'deptCode');
      this.editingRolesForDeptCode = undefined;
      this.alertScreenReader('Role edits saved');
      this.putFocusNextTick('my-dept-roles')
    },
    cancelEditRoles() {
      this.showEditRolesModal = false;
      this.editingRolesForDeptCode = undefined;
      this.alertScreenReader('Dialog closed');
      this.putFocusNextTick('btn-edit-my-dept-roles')
    },
    conditionalAppend(items, item, append) {
      if (append) {
        items.push(item)
      }
    },
    getRoles(department) {
      const dropInAdvisorRole = `Drop-in Advisor${this.isSupervisorOnCall(this.$currentUser, department.code) ? ' (Supervisor On Call)' : ''}`;
      const advisorType = this.includes(this.dropInAdvisorDeptCodes, department.code) ? dropInAdvisorRole : 'Advisor';
      const roles = [];
      this.conditionalAppend(roles, 'Director', department.isDirector);
      this.conditionalAppend(roles, advisorType, department.isAdvisor);
      this.conditionalAppend(roles, 'Scheduler', department.isScheduler);
      return roles;
    },
    openEditRolesModal(deptCode) {
      this.editingRolesForDeptCode = deptCode;
      this.showEditRolesModal = true;
      this.alertScreenReader('Edit roles form is open');
    }
  }
}
</script>
