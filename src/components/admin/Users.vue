<template>
  <div>
    <b-container fluid class="mb-2">
      <b-row align-v="center" no-gutters>
        <b-col cols="2" class="pr-2">
          <b-form-select
            id="user-filter-options"
            v-model="filterType"
            :disabled="isBusy"
            :options="[
              {text: 'BOA Admins', value: 'admins'},
              {text: 'Search', value: 'search'},
              {text: 'Filter', value: 'filter'}
            ]"
            @change="$refs.users.refresh()"></b-form-select>
        </b-col>
        <b-col v-if="filterType === 'search'" cols="10">
          <Autocomplete
            id="search-user"
            v-model="userSelection"
            :disabled="isBusy"
            :source="autocompleteUsers"
            dropdown-class="w-100"
            class="w-50"
            placeholder="Name or UID...">
          </Autocomplete>
        </b-col>
        <b-col v-if="filterType === 'filter'">
          <div class="d-flex">
            <div class="pr-2">
              <b-form-select
                id="department-select-list"
                v-model="filterBy.deptCode"
                :disabled="isBusy"
                :options="departments"
                value-field="code"
                text-field="name"
                aria-label="Use up and down arrows to review departments. Hit enter to select a department."
                @change="$refs.users.refresh()">
                <template v-slot:first>
                  <option :value="null">All</option>
                </template>
              </b-form-select>
            </div>
            <div class="pr-2">
              <b-form-select
                id="user-permission-options"
                v-model="filterBy.role"
                :disabled="isBusy"
                :options="[
                  {text: 'All', value: null},
                  {text: 'Advisors', value: 'advisor'},
                  {text: 'No Canvas Data', value: 'noCanvasDataAccess'},
                  {text: 'No Notes or Appointments', value: 'noAdvisingDataAccess'},
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
                :disabled="isBusy"
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
    <div class="align-items-center d-flex pl-4">
      <div>
        <strong>Quick links:</strong>
      </div>
      <div>
        <b-btn
          id="quick-link-directors"
          :disabled="isBusy"
          class="pl-2 pr-2"
          variant="link"
          @click="quickLink('director')">
          Directors
        </b-btn>
      </div>
      <div>
        |
      </div>
      <div>
        <b-btn
          id="quick-link-drop-in-advisors"
          :disabled="isBusy"
          class="pl-2 pr-2"
          variant="link"
          @click="quickLink('dropInAdvisor')">
          Drop-in Advisors
        </b-btn>
      </div>
      <div>
        |
      </div>
      <div>
        <b-btn
          id="quick-link-advisors"
          :disabled="isBusy"
          class="pl-2 pr-2"
          variant="link"
          @click="quickLink('advisor', 'QCADV')">
          L&amp;S Advisors
        </b-btn>
      </div>
      <div>
        |
      </div>
      <div>
        <b-btn
          id="quick-link-schedulers"
          :disabled="isBusy"
          class="pl-2 pr-2"
          variant="link"
          @click="quickLink('scheduler')">
          Schedulers
        </b-btn>
      </div>
    </div>
    <div class="font-size-14 mb-3 ml-4 total-user-count">
      <span v-if="totalUserCount === 0">No users found</span>
      <span v-if="totalUserCount > 0">{{ pluralize('user', totalUserCount) }}</span>
    </div>
    <b-table
      id="users-table"
      ref="users"
      :busy.sync="isBusy"
      :fields="[
        {key: 'toggleDetails', label: '', class: 'column-toggle-details'},
        {key: 'uid', class: 'column-uid'},
        {key: 'edit', class: 'column-edit', thClass: 'color-transparent', variant: 'primary'},
        {key: 'lastName', class: 'column-name font-weight-bolder pl-1', sortable: true, variant: 'primary'},
        {key: 'depts', label: 'Department(s)'},
        {key: 'status', class: 'column-status'},
        {key: 'lastLogin', class: 'column-last-login', sortable: true, variant: 'info'},
        {key: 'email', class: 'column-email text-center'},
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
          class="column-toggle-details-button"
          variant="link"
          @click="row.toggleDetails">
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
      <template v-slot:cell(edit)="row">
        <EditUserProfileModal
          :after-update-user="afterUpdateUser"
          :departments="departments"
          :profile="row.item" />
      </template>
      <template v-slot:cell(lastName)="row">
        <div class="d-flex">
          <div v-if="!row.item.canAccessCanvasData" class="text-secondary pr-2 position-relative">
            <span>C</span>
            <font-awesome
              :id="`permission-canvas-data-${row.item.uid}`"
              class="icon-slash"
              title="Cannot access Canvas data"
              icon="slash" />
          </div>
          <div v-if="!row.item.canAccessAdvisingData" class="text-secondary pr-2 position-relative">
            <font-awesome
              :id="`permission-advising-data-${row.item.uid}`"
              :icon="['far', 'sticky-note']" />
            <font-awesome
              :id="`permission-advising-data-${row.item.uid}`"
              class="icon-slash"
              title="Cannot access Advising data"
              icon="slash" />
          </div>
          <div v-if="row.item.name">
            <span class="sr-only">Name</span>
            <a
              :id="`directory-link-${row.item.uid}`"
              :aria-label="`Go to UC Berkeley Directory page of ${row.item.name}`"
              :href="`https://www.berkeley.edu/directory/results?search-term=${row.item.name}`"
              class="m-0"
              target="_blank">
              {{ row.item.name }}
            </a>
          </div>
          <div v-if="!row.item.name">
            <span class="faint-text">(Name unavailable)</span>
          </div>
        </div>
      </template>
      <template v-slot:cell(depts)="row">
        <div v-for="department in row.item.departments" :key="department.code" class="pb-1">
          <font-awesome
            v-if="!department.automateMembership"
            class="text-warning pr-1"
            title="Membership is not automated"
            icon="exclamation-triangle" />
          <span :id="`dept-${department.code}-${row.item.uid}`">
            <span class="dept-name">{{ department.name }}</span> ({{ oxfordJoin(getBoaUserRoles(row.item, department)) }})
          </span>
        </div>
        <div v-if="row.item.isAdmin" class="dept-name">BOA Admin</div>
      </template>
      <template v-slot:cell(status)="row">
        <span :id="`user-status-${row.item.uid}`">{{ oxfordJoin(getUserStatuses(row.item)) }}</span>
      </template>
      <template v-slot:cell(lastLogin)="row">
        <span v-if="row.item.lastLogin" :id="`user-last-login-${row.item.uid}`">{{ row.item.lastLogin | moment('MMM D, YYYY') }}</span>
      </template>
      <template v-slot:cell(email)="row">
        <span :id="`user-email-${row.item.uid}`">
          <a
            :aria-label="`Send email to ${row.item.name}`"
            :href="`mailto:${row.item.campusEmail}`"
            target="_blank"><font-awesome icon="envelope" /><span class="sr-only"> (will open new browser tab)</span></a>
        </span>
      </template>
      <template v-slot:row-details="row">
        <b-card>
          <pre :id="`user-details-${row.item.uid}`">{{ row.item }}</pre>
        </b-card>
      </template>
      <template v-slot:cell(actions)="row">
        <b-btn
          v-if="canBecome(row.item)"
          :id="'become-' + row.item.uid"
          :title="`Log in as ${row.item.name}`"
          variant="link"
          @click="become(row.item.uid)">
          <font-awesome icon="sign-in-alt" />
        </b-btn>
      </template>
    </b-table>
  </div>
</template>

<script>
import Autocomplete from '@/components/util/Autocomplete';
import Berkeley from '@/mixins/Berkeley';
import Context from '@/mixins/Context';
import EditUserProfileModal from '@/components/admin/EditUserProfileModal';
import Util from '@/mixins/Util';
import { becomeUser, getAdminUsers, getUserByUid, getUsers, userAutocomplete } from '@/api/user';

export default {
  name: 'Users',
  components: {Autocomplete, EditUserProfileModal},
  mixins: [Berkeley, Context, Util],
  props: {
    departments: {
      required: true,
      type: Array
    },
    refresh: {
      default: false,
      required: false,
      type: Boolean
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
    totalUserCount: undefined,
    userSelection: undefined
  }),
  watch: {
    refresh(value) {
      if (value) {
        this.$refs.users.refresh();
      }
    },
    userSelection(u) {
      if (u) {
        this.$refs.users.refresh();
      }
    }
  },
  methods: {
    afterUpdateUser(profile) {
      this.alertScreenReader(`${profile.name} profile updated.`);
      if (this.filterType === 'search') {
        this.userSelection = profile;
      }
      this.$refs.users.refresh();
    },
    autocompleteUsers(q) {
      return userAutocomplete(q).then(results => this.orderBy(results, 'label'));
    },
    become(uid) {
      becomeUser(uid).then(() => (window.location.href = '/home'));
    },
    canBecome(user) {
      const isNotMe = user.uid !== this.$currentUser.uid;
      const expiredOrInactive = user.isExpiredPerLdap || user.deletedAt || user.isBlocked;
      const hasAnyRole = user.isAdmin || this.find(user.departments, (dept) => !this.isNil(dept.role));
      return this.$config.devAuthEnabled && isNotMe && !expiredOrInactive && hasAnyRole;
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
    openEditUserModal(user) {
      user.showEditUserModal = true;
    },
    quickLink(role, deptCode=null) {
      this.filterType = 'filter';
      this.filterBy = {
        deptCode: deptCode,
        role: role,
        searchPhrase: '',
        status: 'active'
      };
      this.$refs.users.refresh();
    },
    usersProvider() {
      this.totalUserCount = undefined;
      let promise = undefined;
      switch(this.filterType) {
      case 'admins':
        promise = getAdminUsers(this.sortBy, this.sortDescending, false).then(data => {
          this.totalUserCount = data.totalUserCount;
          return data.users;
        });
        break;
      case 'filter':
        promise = getUsers(
          this.isNil(this.filterBy.status) ? null : this.filterBy.status === 'blocked',
          this.isNil(this.filterBy.status) ? null : this.filterBy.status === 'deleted',
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
        if (this.userSelection) {
          promise = getUserByUid(this.userSelection.uid, false).then(data => {
            this.totalUserCount = 1;
            this.userSelection = undefined;
            return [ data ];
          });
        } else {
          promise = new Promise(resolve => resolve([]));
        }
        this.putFocusNextTick('search-user-input');
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
.color-transparent {
  color: transparent;
}
.column-actions {
  width: 50px;
}
.column-edit {
  padding: 3px 2px 0 4px !important;
  width: 30px;
}
.column-email {
  width: 50px;
}
.column-last-login {
  width: 120px;
}
.column-name {
  width: 200px;
}
.column-status {
  width: 100px;
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
  width: 140px;
}
.dept-name {
  color: #484;
  font-weight: 500;
}
.icon-slash {
  color: #cf1715;
  left: -4px;
  position: absolute;
  top: 4px;
}
.position-relative {
  position: relative;
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
</style>
