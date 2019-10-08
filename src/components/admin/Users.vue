<template>
  <div class="list-group">
    <h2 id="dept-users-section" class="page-section-header-sub pb-2">
      Users
      <span class="text-black-50 font-size-14">(<a id="download-boa-users-csv" :href="`${apiBaseUrl}/api/users/csv`">download</a>)</span>
    </h2>
    <b-container class="pl-0 ml-0">
      <b-form-row class="pb-2">
        <b-col>
          <b-form-select
            v-if="departments.length"
            id="department-select-list"
            v-model="filter"
            :options="departments"
            value-field="code"
            text-field="name"
            role="listbox"
            aria-label="Use up and down arrows to review departments. Hit enter to select a department.">
            <template v-slot:first>
              <option :value="null" disabled>-- Select a department --</option>
            </template>
          </b-form-select>
        </b-col>
        <b-col>
          <b-input-group-append>
            <b-button 
              :disabled="!filter" 
              @click="clearFilter">
              Clear Filter
            </b-button>
          </b-input-group-append>
        </b-col>
      </b-form-row>
    </b-container>
    <b-table
      id="users-table"
      :fields="fields"
      :filter="filter"
      :filter-function="filterUsers"
      :filter-included-fields="filterFields"
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
        <div>{{ row.item.uid }}</div>
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
        <div>{{ row.item.title }}</div>
      </template>
      <template slot="depts" slot-scope="row">
        <div
          v-for="deptCode in keys(row.item.departments)"
          :key="deptCode">
          <span>{{ row.item.departments[deptCode]['deptName'] }}</span>
        </div>
      </template>
      <template slot="campusEmail" slot-scope="row">
        <div>{{ row.item.campusEmail }}</div>
      </template>
      <template slot="row-details" slot-scope="row">
        <b-card>
          <b-container>
            <b-row>
              <b-col>
                <h3 class="user-details-header">Permissions</h3>
                <ul class="flex-container flex-col">
                  <li>{{ row.item.canAccessCanvasData ? 'Canvas data access' : 'No Canvas data' }}</li>
                  <li v-if="row.item.isAdmin">Admin</li>
                  <li v-if="row.item.isAdmin">Admin</li>
                </ul>
              </b-col>
              <b-col>
                <h3 class="user-details-header">Status</h3>
                <ul class="flex-container flex-col">
                  <li>{{ row.item.deletedAt ? 'Deleted' : 'Active' }}</li>
                  <li v-if="row.item.isBlocked">Blocked</li>
                  <li v-if="row.item.isExpiredPerLdap">Expired account (according to CalNet)</li>
                </ul>
              </b-col>
              <b-col cols="8">
                <h3 class="user-details-header">Department Membership</h3>
                <div v-if="isEmpty(row.item.departments)">None</div>
                <table v-if="!isEmpty(row.item.departments)" class="user-dept-membership-table">
                  <tr 
                    v-for="deptCode in keys(row.item.departments)"
                    :key="deptCode">
                    <th scope="row">{{ row.item.departments[deptCode]['deptName'] }}</th>
                    <td>{{ deptRoles(row.item.departments[deptCode]) }}</td>
                    <td>{{ row.item.departments[deptCode]['automateMembership'] ? 'Automated' : 'Manual' }} Membership</td>
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
            v-if="devAuthEnabled && (row.item.uid !== user.uid) && !row.item.isExpiredPerLdap"
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
    departments: Array,
    users: Array
  },
  data: () => ({
    currentPage: 1,
    fields: [
      {key: 'toggleDetails', label: '', class: 'user-details-toggle'},
      {key: 'uid', sortable: true, class: 'user-uid'},
      {key: 'name', sortable: true},
      {key: 'title', sortable: true},
      {key: 'depts', label: 'Department(s)'},
      {key: 'campusEmail'},
      {key: 'actions', label: '', class: 'user-actions'}
    ],
    filter: null,
    filterFields: ['depts'],
    items: [],
    perPage: 10,
    rowCount: 0,
    sortBy: 'lastName',
    sortDesc: false
  }),
  created() {
    this.items = this.cloneDeep(this.users);
    this.rowCount = this.users ? this.size(this.users) : 0;
  },
  methods: {
    become(uid) {
      becomeUser(uid).then(() => (window.location.href = '/home'));
    },
    clearFilter() {
      this.filter = null;
    },
    deptRoles(dept) {
      let roles = []
      if (this.get(dept, 'isAdvisor')) {
        roles.push('Advisor');
      }
      if (this.get(dept, 'isDirector')) {
        roles.push('Director');
      }
      return this.oxfordJoin(roles);
    },
    filterUsers(user, filter) {
      return this.includes(this.keys(user.departments), filter);
    },
    onFilter(filteredItems) {
      this.rowCount = filteredItems.length
      this.currentPage = 1
    },
    openEdit() {
      //TODO: BOAC-2844
      return false;
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
