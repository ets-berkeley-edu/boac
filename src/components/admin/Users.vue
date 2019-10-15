<template>
  <div class="list-group">
    <h2 id="dept-users-section" class="page-section-header-sub pb-2">
      Users
      <span class="text-black-50 font-size-14">(<a id="download-boa-users-csv" :href="`${apiBaseUrl}/api/users/csv`">download</a>)</span>
    </h2>
    <b-container class="pl-0 ml-0">
      <b-form-row class="pb-2">
        <b-col cols="6" class="mr-5">
          <b-form-group>
            <b-form-input
              id="user-name-uid-search"
              v-model="filterNameUid"
              class="mb-3"
              type="search"
              placeholder="Name or UID">
            </b-form-input>
            <b-form-select
              v-if="departments.length"
              id="department-select-list"
              v-model="filterDept"
              :options="departments"
              value-field="code"
              text-field="name"
              role="listbox"
              aria-label="Use up and down arrows to review departments. Hit enter to select a department."
              @change="isResetDisabled=false">
              <template v-slot:first>
                <option :value="null" disabled>-- Select a department --</option>
                <option :value="'ALL'">All Departments</option>
              </template>
            </b-form-select>
          </b-form-group>
        </b-col>
        <b-col>
          <b-form-group>
            <b-form-checkbox-group
              id="user-permission-options"
              v-model="filterPermissions"
              :options="userPermissionOptions"
              name="user-permission-options"
              stacked
              @change="isResetDisabled=false">
            </b-form-checkbox-group>
          </b-form-group>
        </b-col>
        <b-col>
          <b-form-group>
            <b-form-checkbox-group
              id="user-status-options"
              v-model="filterStatuses"
              :options="userStatusOptions"
              name="user-status-options"
              stacked
              @change="isResetDisabled=false">
            </b-form-checkbox-group>
          </b-form-group>
        </b-col>
        <b-col>
          <b-input-group-append>
            <b-button
              id="user-filter-reset-button"
              :disabled="isResetDisabled && !filterNameUid"
              @click="resetFilter">
              Reset Filter
            </b-button>
          </b-input-group-append>
        </b-col>
      </b-form-row>
    </b-container>
    <b-table
      id="users-table"
      :fields="fields"
      :filter="filter"
      :filter-function="applyFilter"
      :items="items"
      :no-sort-reset="true"
      :small="true"
      :sort-by.sync="sortBy"
      :sort-compare="sortCompare"
      :sort-desc.sync="sortDesc"
      :per-page="perPage"
      :current-page="currentPage"
      fixed
      primary-key="uid"
      responsive
      sort-icon-left
      stacked="lg"
      tbody-tr-class="font-size-14"
      thead-class="sortable-table-header text-nowrap"
      @filtered="onFilter">
      <template slot="toggleDetails" slot-scope="row">
        <b-btn
          :id="`user-${row.item.uid}-details-toggle`"
          class="user-details-toggle-button"
          variant="link"
          @click="row.toggleDetails">
          <font-awesome v-if="!row.detailsShowing" icon="caret-right" />
          <span v-if="!row.detailsShowing" class="sr-only">Show user details</span>
          <font-awesome v-if="row.detailsShowing" icon="caret-down" />
          <span v-if="row.detailsShowing" class="sr-only">Hide user details</span>
        </b-btn>
      </template>
      <template slot="uid" slot-scope="row">
        <span class="sr-only">U I D</span>
        <div :id="`uid-${row.item.uid}`">{{ row.item.uid }}</div>
      </template>
      <template slot="name" slot-scope="row">
        <span class="sr-only">User name</span>
        <a
          :id="`directory-link-${row.item.uid}`"
          class="user-name"
          :aria-label="`Go to UC Berkeley Directory page of ${row.item.name}`"
          :href="`https://www.berkeley.edu/directory/results?search-term=${row.item.name}`"
          target="_blank">
          {{ row.item.name }}
        </a>
      </template>
      <template slot="title" slot-scope="row">
        <div :id="`title-${row.item.uid}`">{{ row.item.title }}</div>
      </template>
      <template slot="depts" slot-scope="row">
        <div
          v-for="(deptCode, index) in keys(row.item.departments)"
          :key="index">
          <span :id="`dept-${index}-${row.item.uid}`">{{ row.item.departments[deptCode]['deptName'] }}</span>
        </div>
      </template>
      <template slot="campusEmail" slot-scope="row">
        <div :id="`email-${row.item.uid}`">{{ row.item.campusEmail }}</div>
      </template>
      <template slot="row-details" slot-scope="row">
        <b-card>
          <b-container>
            <b-row>
              <b-col>
                <h3 class="user-details-header">Permissions</h3>
                <ul class="flex-container flex-col">
                  <li :id="`permission-canvas-data-${row.item.uid}`" class="text-nowrap">{{ row.item.canAccessCanvasData ? 'Canvas data access' : 'No Canvas data' }}</li>
                  <li v-if="row.item.isAdmin" :id="`permission-admin-${row.item.uid}`">Admin</li>
                </ul>
              </b-col>
              <b-col>
                <h3 class="user-details-header">Status</h3>
                <ul class="flex-container flex-col">
                  <li :id="`status-deleted-${row.item.uid}`">{{ row.item.deletedAt ? 'Deleted' : 'Active' }}</li>
                  <li v-if="row.item.isBlocked" :id="`status-blocked-${row.item.uid}`">Blocked</li>
                  <li v-if="row.item.isExpiredPerLdap" :id="`status-expired-${row.item.uid}`">Expired account (according to CalNet)</li>
                </ul>
              </b-col>
              <b-col cols="8">
                <h3 class="user-details-header">Department Membership</h3>
                <div v-if="isEmpty(row.item.departments)">None</div>
                <table v-if="!isEmpty(row.item.departments)" :id="`user-depts-table-${row.item.uid}`" class="user-dept-membership-table">
                  <tr
                    v-for="(deptCode, index) in keys(row.item.departments)"
                    :key="index">
                    <th :id="`dept-detail-${index}-${row.item.uid}`" scope="row">{{ row.item.departments[deptCode]['deptName'] }}</th>
                    <td :id="`dept-roles-${index}-${row.item.uid}`">{{ deptRoles(row.item.departments[deptCode]) }}</td>
                    <td :id="`dept-membership-${index}-${row.item.uid}`">{{ row.item.departments[deptCode]['automateMembership'] ? 'Automated' : 'Manual' }} Membership</td>
                  </tr>
                </table>
              </b-col>
            </b-row>
          </b-container>
        </b-card>
      </template>
      <template slot="actions" slot-scope="row">
        <div class="flex-row">
          <b-btn
            :id="`user-${row.item.uid}-edit`"
            :disabled="true"
            :title="`Edit user ${row.item.name}`"
            variant="link"
            @click="openEdit">
            <font-awesome icon="edit" />
            <span class="sr-only">Edit user</span>
          </b-btn>
          <b-btn
            v-if="canBecome(row.item)"
            :id="'become-' + row.item.uid"
            :title="`Log in as ${row.item.name}`"
            variant="link"
            @click="become(row.item.uid)">
            <font-awesome icon="sign-in-alt" />
          </b-btn>
        </div>
      </template>
    </b-table>
    <b-pagination
      v-if="items"
      id="users-paginator"
      v-model="currentPage"
      :total-rows="rowCount"
      :per-page="perPage"
      aria-controls="users-table">
    </b-pagination>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { becomeUser } from '@/api/user';

export default {
  name: 'Users',
  mixins: [Context, UserMetadata, Util],
  props: {
    users: Array
  },
  data: () => ({
    currentPage: 1,
    departments: [],
    filterDept: null,
    fields: [
      {key: 'toggleDetails', label: '', class: 'user-details-toggle'},
      {key: 'uid', sortable: true, class: 'user-uid'},
      {key: 'name', sortable: true},
      {key: 'title', sortable: true},
      {key: 'depts', label: 'Department(s)'},
      {key: 'campusEmail'},
      {key: 'actions', label: '', class: 'user-actions'}
    ],
    filter: undefined,
    filterPermissions: [
      'canAccessCanvasData',
      'isAdmin',
      'isAdvisor',
      'isDirector',
      'isDropInAdvisor',
      'isScheduler'
    ],
    filterStatuses: ['isActive'],
    isResetDisabled: true,
    items: [],
    filterNameUid: undefined,
    perPage: 10,
    rowCount: 0,
    sortBy: 'lastName',
    sortDesc: false,
    userPermissionOptions: [
      {text: 'Admins', value: 'isAdmin'},
      {text: 'Advisors', value: 'isAdvisor'},
      {text: 'Canvas Access', value: 'canAccessCanvasData'},
      {text: 'Directors', value: 'isDirector'},
      {text: 'Drop-In Advisors', value: 'isDropInAdvisor'},
      {text: 'Schedulers', value: 'isScheduler'}
    ],
    userStatusOptions: [
      {text: 'Active', value: 'isActive'},
      {text: 'Deleted', value: 'deletedAt'},
      {text: 'Blocked', value: 'isBlocked'},
      {text: 'Expired', value: 'isExpiredPerLdap'}
    ]
  }),
  mounted() {
    this.items = this.cloneDeep(this.users);
    this.departments = this.orderBy(this.uniqBy(this.flatMap(this.users, this.getDepartments), 'code'), 'name');
    this.filter = this.concat(this.filterNameUid, this.filterDept, this.filterPermissions, this.filterStatuses);
    this.rowCount = this.users ? this.size(this.users) : 0;
  },
  methods: {
    applyFilter(user) {
      const activeMatch = this.includes(this.filterStatuses, 'isActive') && !user.deletedAt && !user.isBlocked;
      const adminMatch = this.includes(this.filterPermissions, 'isAdmin') && user.isAdmin;
      const advisorMatch = this.includes(this.filterPermissions, 'isAdvisor') &&  this.find(user.departments, (dept) => dept.isAdvisor);
      const blockedMatch = this.includes(this.filterStatuses, 'isBlocked') && user.isBlocked;
      const canvasAccessMatch = this.includes(this.filterPermissions, 'canAccessCanvasData') && user.canAccessCanvasData;
      const deletedMatch = this.includes(this.filterStatuses, 'deletedAt') && user.deletedAt;
      const deptMatch = !this.filterDept || this.filterDept === 'ALL' || this.includes(this.keys(user.departments), this.filterDept);
      const directorMatch = this.includes(this.filterPermissions, 'isDirector') && this.find(user.departments, (dept) => dept.isDirector);
      const dropInAdvisorMatch = this.includes(this.filterPermissions, 'isDropInAdvisor') && this.find(user.departments, (dept) => dept.isDropInAdvisor);
      const expiredMatch = this.includes(this.filterStatuses, 'isExpiredPerLdap') && user.isExpiredPerLdap;
      const nameUidMatch = !this.filterNameUid || this.includes(user.name.toLowerCase(), this.filterNameUid.toLowerCase()) || this.includes(user.uid, this.filterNameUid);
      const noPermissionsMatch = this.isEmpty(this.filterPermissions) && !user.isAdmin && !this.find(user.departments, (dept) => dept.isAdvisor || dept.isDirector || dept.isDropInAdvisor || dept.isScheduler);
      const schedulerMatch = this.includes(this.filterPermissions, 'isScheduler') && this.find(user.departments, (dept) => dept.isScheduler);

      const permissionsMatch = adminMatch || advisorMatch || canvasAccessMatch || directorMatch || dropInAdvisorMatch || schedulerMatch || noPermissionsMatch;
      const statusMatch = activeMatch || deletedMatch || blockedMatch || expiredMatch;

      return nameUidMatch && deptMatch && permissionsMatch && statusMatch;
    },
    become(uid) {
      becomeUser(uid).then(() => (window.location.href = '/home'));
    },
    canBecome(user) {
      const isNotMe = user.uid !== this.user.uid;
      const expiredOrInactive = user.isExpiredPerLdap || user.deletedAt || user.isBlocked;
      const hasAnyRole = find(user.departments, (dept) => dept.isAdvisor || dept.isDirector || dept.isDropInAdvisor || dept.isScheduler);
      this.devAuthEnabled && isNotMe && !expiredOrInactive && hasAnyRole;
    },
    deptRoles(dept) {
      let roles = [];
      this.each([
        {key: 'isAdvisor', label: 'Advisor'},
        {key: 'isDirector', label: 'Director'},
        {key: 'isDropInAdvisor', label: 'Drop-In Advisor'},
        {key: 'isScheduler', label: 'Scheduler'}
      ], role => {
        if (this.get(dept, role.key)) {
          roles.push(role.label);
        }
      });
      return this.size(roles) ? this.oxfordJoin(roles) : '';
    },
    getDepartments(user) {
      return this.map(user.departments, function(dept, deptCode) {
        return {code: deptCode, name: dept.deptName};
      });
    },
    onFilter(filteredItems) {
      const newRowCount = this.size(filteredItems);
      if (newRowCount !== this.rowCount) {
        this.currentPage = 1;
      }
      this.rowCount = newRowCount;
    },
    openEdit() {
      //TODO: BOAC-2844
      return false;
    },
    resetFilter() {
      this.filterNameUid = null;
      this.filterDept = null;
      this.filterPermissions = ['canAccessCanvasData', 'isAdmin', 'isAdvisor', 'isDirector', 'isDropInAdvisor', 'isScheduler'];
      this.filterStatuses = ['isActive'];
      this.isResetDisabled = true;
    },
    sortCompare(a, b, sortBy) {
      const key = sortBy === 'name' ? 'lastName' : sortBy
      let aValue = this.get(a, key);
      let bValue = this.get(b, key);
      return this.sortComparator(aValue, bValue);
    }
  }
}
</script>

<style>
.user-actions {
  width: 96px;
}
.user-dept-membership-table td {
  border: none;
  padding: 5px 20px 5px 0;
}
.user-dept-membership-table th {
  border: none;
  color: #aaa;
  font-weight: normal;
  padding: 5px 20px 5px 0;
}
.user-details-header {
  color: #aaa;
  font-size: 13px;
  font-weight: normal;
  vertical-align: top;
}
.user-details-toggle {
  width: 25px;
}
.user-details-toggle-button {
  color: #337ab7;
  height: 15px;
  line-height: 1;
  margin-right: 10px;
  padding: 0;
}
.user-name {
  color: #49b;
  margin: 0;
}
.user-uid {
  width: 75px;
}
</style>
