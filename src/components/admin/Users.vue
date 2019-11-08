<template>
  <div>
    <b-container fluid class="mb-2">
      <b-row align-v="center" no-gutters>
        <b-col cols="2" class="pr-2">
          <b-form-select
            id="user-permission-options"
            v-model="filterType"
            :options="[
              {text: 'BOA Admins', value: 'admins'},
              {text: 'Search', value: 'search'},
              {text: 'Filter', value: 'filter'}
            ]"
            @change="$refs.users.refresh()"></b-form-select>
        </b-col>
        <b-col v-if="filterType === 'search'" cols="10">
          <div class="d-flex">
            <div class="pr-2 w-50">
              <b-form-input
                id="user-search"
                v-model="filterBy.searchPhrase"
                type="search"
                placeholder="UID or Name"></b-form-input>
            </div>
            <div>
              <b-btn
                id="user-search-btn"
                :disabled="!trim(filterBy.searchPhrase).length"
                @keyup.enter="$refs.users.refresh()"
                @click="$refs.users.refresh()">
                Search
              </b-btn>
            </div>
          </div>
        </b-col>
        <b-col v-if="filterType === 'filter'">
          <div class="d-flex">
            <div class="pr-2">
              <b-form-select
                id="department-select-list"
                v-model="filterBy.deptCode"
                :options="departments"
                @change="$refs.users.refresh()"
                value-field="deptCode"
                text-field="deptName"
                aria-label="Use up and down arrows to review departments. Hit enter to select a department.">
                <template v-slot:first>
                  <option :value="null">All</option>
                </template>
              </b-form-select>
            </div>
            <div class="pr-2">
              <b-form-select
                id="user-permission-options"
                v-model="filterBy.role"
                :options="[
                  {text: 'All', value: null},
                  {text: 'Advisors', value: 'advisor'},
                  {text: 'No Canvas Data', value: 'noCanvasDataAccess'},
                  {text: 'Directors', value: 'director'},
                  {text: 'Drop-In Advisors', value: 'dropInAdvisor'},
                  {text: 'Schedulers', value: 'scheduler'}
                ]"
                @change="$refs.users.refresh()"></b-form-select>
            </div>
            <div class="pr-2">
              <b-form-select
                id="user-status-options"
                v-model="filterBy.status"
                :options="[
                  {text: 'All', value: null},
                  {text: 'Active', value: 'active'},
                  {text: 'Deleted', value: 'deleted'},
                  {text: 'Blocked', value: 'blocked'}
                ]"
                @change="$refs.users.refresh()"></b-form-select>
            </div>
          </div>
        </b-col>
      </b-row>
    </b-container>
    <div class="font-size-14 mb-2 ml-4 total-user-count">
      <span v-if="totalUserCount === 0">No users found</span>
      <span v-if="totalUserCount > 0">{{ 'user' | pluralize(totalUserCount) }}</span>
    </div>
    <b-table
      id="users-table"
      ref="users"
      :busy.sync="isBusy"
      :fields="[
        {key: 'toggleDetails', label: '', class: 'column-toggle-details'},
        {key: 'uid', class: 'column-uid'},
        {key: 'lastName', class: 'column-name', sortable: true, variant: 'primary'},
        {key: 'depts', label: 'Department(s)'},
        {key: 'email', class: 'column-email'},
        {key: 'status', class: 'column-status'},
        {key: 'actions', class: 'p-0 pt-1 column-actions', label: ''}
      ]"
      :items="usersProvider"
      :current-page="currentPage"
      :sort-by.sync="sortBy"
      :no-sort-reset="true"
      :sort-desc.sync="sortDescending"
      fixed
      hover
      responsive
      sort-icon-left
      stacked="md"
      striped
      thead-class="sortable-table-header text-nowrap">
      <template v-slot:cell(toggleDetails)="row">
        <b-btn
          :id="`user-${row.item.uid}-details-toggle`"
          @click="row.toggleDetails"
          class="column-toggle-details-button"
          variant="link">
          <font-awesome v-if="!row.detailsShowing" icon="caret-right" />
          <span v-if="!row.detailsShowing" class="sr-only">Show user details</span>
          <font-awesome v-if="row.detailsShowing" icon="caret-down" />
          <span v-if="row.detailsShowing" class="sr-only">Hide user details</span>
        </b-btn>
      </template>
      <template v-slot:cell(uid)="row">
        <span class="sr-only">U I D</span>
        <span :id="`uid-${row.item.uid}`">{{ row.item.uid }}</span>
      </template>
      <template v-slot:cell(lastName)="row">
        <span class="sr-only">Name</span>
        <a
          :id="`directory-link-${row.item.uid}`"
          :aria-label="`Go to UC Berkeley Directory page of ${row.item.name}`"
          :href="`https://www.berkeley.edu/directory/results?search-term=${row.item.name}`"
          class="m-0"
          target="_blank">
          {{ row.item.name }}
        </a>
      </template>
      <template v-slot:cell(depts)="row">
        <div v-for="deptCode in keys(row.item.departments)" :key="deptCode" class="pb-1">
          <font-awesome
            v-if="!row.item.departments[deptCode].automateMembership"
            class="has-error pr-1"
            title="Membership is not automated"
            icon="exclamation-triangle" />
          <span :id="`dept-${deptCode}-${row.item.uid}`">
            <span class="dept-name">{{ row.item.departments[deptCode]['deptName'] }}</span> ({{ oxfordJoin(getDeptRoles(row.item, deptCode)) }})
          </span>
        </div>
        <div v-if="row.item.isAdmin" class="dept-name">BOA Admin</div>
      </template>
      <template v-slot:cell(email)="row">
        <span :id="`user-email-${row.item.uid}`">
          <a
            :aria-label="`Send email to ${row.item.name}`"
            :href="`mailto:${row.item.campusEmail}`"
            target="_blank">{{ row.item.campusEmail }}<span class="sr-only"> (will open new browser tab)</span></a>
        </span>
      </template>
      <template v-slot:cell(status)="row">
        <span :id="`user-status-${row.item.uid}`">{{ oxfordJoin(getUserStatuses(row.item)) }}</span>
      </template>
      <template v-slot:row-details="row">
        <b-card>
          <div v-if="!row.item.canAccessCanvasData" :id="`permission-canvas-data-${row.item.uid}`" class="has-error text-nowrap">Cannot access Canvas data.</div>
          <div><span class="font-weight-500">Last login:</span> {{ row.item.lastLogin }}</div>
        </b-card>
      </template>
      <template v-slot:cell(actions)="row">
        <b-btn
          v-if="canBecome(row.item)"
          :id="'become-' + row.item.uid"
          :title="`Log in as ${row.item.name}`"
          @click="become(row.item.uid)"
          variant="link">
          <font-awesome icon="sign-in-alt" />
        </b-btn>
      </template>
    </b-table>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { becomeUser, getAdminUsers, getUsers, userSearch } from '@/api/user';

export default {
  name: 'Users',
  mixins: [Context, UserMetadata, Util],
  props: {
    departments: {
      required: true,
      type: Array
    }
  },
  data: () => ({
    currentPage: 1,
    filterBy: {
      deptCode: 'QCADV',
      role: null,
      searchPhrase: '',
      status: null
    },
    filterType: 'search',
    isBusy: false,
    sortBy: 'lastName',
    sortDescending: false,
    totalUserCount: undefined
  }),
  methods: {
    become(uid) {
      becomeUser(uid).then(() => (window.location.href = '/home'));
    },
    canBecome(user) {
      const isNotMe = user.uid !== this.user.uid;
      const expiredOrInactive = user.isExpiredPerLdap || user.deletedAt || user.isBlocked;
      const hasAnyRole = user.isAdmin || this.find(user.departments, (dept) => dept.isAdvisor || dept.isDirector || dept.isScheduler);
      return this.devAuthEnabled && isNotMe && !expiredOrInactive && hasAnyRole;
    },
    deptRoles(dept) {
      let roles = [];
      this.each([
        {key: 'advisor', label: 'Advisor'},
        {key: 'director', label: 'Director'},
        {key: 'scheduler', label: 'Scheduler'}
      ], role => {
        if (this.get(dept, role.key)) {
          roles.push(role.label);
        }
      });
      return this.size(roles) ? this.oxfordJoin(roles) : '';
    },
    getDeptRoles(user, deptCode) {
      const roles = [];
      const d = user.departments[deptCode];
      if (d.isAdvisor) {
        roles.push('Advisor');
      }
      if (this.find(user.dropInAdvisorStatus, ['deptCode', deptCode])) {
        roles.push('Drop-in Advisor');
      }
      if (d.isDirector) {
        roles.push('Director');
      }
      if (d.isScheduler) {
        roles.push('Scheduler');
      }
      return roles;
    },
    getUserStatuses(user) {
      const statuses = user.deletedAt ? [ 'Deleted' ] : [ 'Active' ];
      if (user.isBlocked) {
        statuses.push('Blocked');
      }
      if (user.isExpiredPerLdap) {
        statuses.push('Expired, according to CalNet.')
      }
      return statuses;
    },
    usersProvider() {
      this.totalUserCount = undefined;
      let promise = undefined;
      switch(this.filterType) {
        case 'admins':
          promise = getAdminUsers(this.sortBy, this.sortDescending).then(data => {
            this.totalUserCount = data.totalUserCount;
            return data.users;
          });
          break;
        case 'filter':
          promise = getUsers(
            this.filterBy.status === 'blocked',
            this.filterBy.status === 'deleted',
            this.filterBy.deptCode,
            this.filterBy.role,
            this.sortBy,
            this.sortDescending
          ).then(data => {
            this.totalUserCount = data.totalUserCount;
            return data.users;
          });
          break;
        case 'search':
          if (this.trim(this.filterBy.searchPhrase)) {
            promise = userSearch(this.filterBy.searchPhrase).then(data => {
              this.totalUserCount = data.totalUserCount;
              return data.users;
            });
          } else {
            promise = new Promise(resolve => resolve([]));
          }
          this.putFocusNextTick('user-search');
          break;
        default:
          promise = new Promise(resolve => resolve([]));
      }
      return promise;
    }
  }
}
</script>

<style>
.column-actions {
  width: 50px;
}
.column-name {
  width: 200px;
}
.column-status {
  width: 120px;
}
.column-toggle-details {
  width: 25px;
}
.column-toggle-details-button {
  color: #337ab7;
  height: 15px;
  line-height: 1;
  margin-right: 10px;
  padding: 0;
}
.column-uid {
  width: 100px;
}
.dept-name {
  color: #484;
  font-weight: 500;
}
.total-user-count {
  max-height: 20px;
  min-height: 20px;
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
</style>
