<template>
  <div>
    <v-container fluid>
      <v-row align-v="center" no-gutters>
        <v-col cols="2" class="pr-2">
          <div class="custom-select-container">
            <select
              id="user-filter-options"
              v-model="filterType"
              class="custom-select"
              :disabled="isBusy"
              @change="refreshUsers"
            >
              <option
                v-for="option in filterTypeOptions"
                :key="option.value"
                :value="option.value"
              >
                {{ option.name }}
              </option>
            </select>
          </div>
        </v-col>
        <v-col v-if="filterType === 'search'" cols="10">
          <span id="user-search-input" class="sr-only">Search for user. Expect auto-suggest as you type name or UID.</span>
          <Autocomplete
            id="search-user-input"
            v-model="userSelection"
            :compact="true"
            :disabled="isBusy"
            :fetch="userAutocomplete"
            :showNoData="true"
            option-label-key="label"
            option-value-key="uid"
            placeholder="Enter name..."
            @user-selected="userSelected"
          />
        </v-col>
        <v-col v-if="filterType === 'filter'">
          <div class="d-flex">
            <div class="pr-2">
              <v-select
                id="department-select-list"
                v-model="filterBy.deptCode"
                aria-label="Use up and down arrows to review departments. Hit enter to select a department."
                :disabled="isBusy"
                :items="departmentSelectionList"
                item-title="name"
                item-value="code"
                variant="outlined"
                density="compact"
                style="font-size: 16px;"
                @update:model-value="refreshUsers"
              >
              </v-select>
            </div>
            <div class="pr-2">
              <v-select
                id="user-permission-options"
                v-model="filterBy.role"
                :disabled="isBusy"
                :items="userPermissionOptions"
                item-title="name"
                item-value="value"
                variant="outlined"
                density="compact"
                style="font-size: 16px;"
                @update:model-value="refreshUsers"
              >
              </v-select>
            </div>
            <div class="pr-2">
              <v-select
                id="user-status-options"
                v-model="filterBy.status"
                :disabled="isBusy"
                :items="userStatusOptions"
                item-title="name"
                item-value="value"
                variant="outlined"
                density="compact"
                style="font-size: 16px;"
                @update:model-value="refreshUsers"
              >
              </v-select>
            </div>
          </div>
        </v-col>
      </v-row>
    </v-container>
    <div class="align-items-center d-flex pl-4">
      <div>
        <strong>Quick links:</strong>
      </div>
      <div>
        <v-btn
          id="quick-link-directors"
          :disabled="isBusy"
          class="pl-2 pr-2 pb-3 text-primary"
          variant="text"
          @click="quickLink('advisor', 'ZCEEE')"
        >
          CE3
        </v-btn>
      </div>
      <div>
        |
      </div>
      <div>
        <v-btn
          id="quick-link-coe-advisors"
          :disabled="isBusy"
          class="pl-2 pr-2 pb-3 text-primary"
          color="	#0096FF"
          variant="text"
          @click="quickLink('advisor', 'COENG')"
        >
          College of Engineering
        </v-btn>
      </div>
      <div>
        |
      </div>
      <div>
        <v-btn
          id="quick-link-qcadv-advisors"
          :disabled="isBusy"
          class="pl-2 pr-2 pb-3 text-primary"
          variant="text"
          @click="quickLink('advisor', 'QCADV')"
        >
          L&amp;S Advisors
        </v-btn>
      </div>
    </div>
    <div class="font-size-14 mv-3 ml-4 total-user-count mb-4">
      <span v-if="totalUserCount === undefined">Loading...</span>
      <span v-if="totalUserCount === 0">No users found</span>
      <span v-if="totalUserCount > 0">{{ pluralize('user', totalUserCount) }}</span>
    </div>
    <v-data-table-server
      v-model:expanded="expanded"
      v-model:items-per-page="itemsPerPage"
      :items="users"
      :items-length="totalUserCount"
      :items-per-page="0"
      :headers="tableHeaders"
      loading-text="Loading users... Please wait."
      :loading="totalUserCount === undefined"
      item-value="uid"
      show-expand
      :hide-default-footer="true"
      disable-pagination
      @update:sort-by="handleSort"
      @update:sort-desc="handleSort"
    >
      <template #item.uid="{ item }">
        <span> {{ item.uid }}</span>
      </template>

      <template #expanded-row="{ columns, item }">
        <tr>
          <td :colspan="columns.length">
            <pre>{{ JSON.stringify(item, null, 2) }}</pre>
          </td>
        </tr>
      </template>

      <template #item.edit="{ item }">
        <EditUserProfileModal
          :after-update-user="afterUpdateUser"
          :departments="departments"
          :profile="item"
        />
      </template>

      <template #item.lastName="{ item }">
        <div v-if="!item.name">
          <span class="faint-text">(Name unavailable)</span>
        </div>
        <div v-if="item.name">
          <a
            :id="`directory-link-${item.uid}`"
            :aria-label="`Go to UC Berkeley Directory page of ${item.name}`"
            :href="`https://www.berkeley.edu/directory/results?search-term=${item.name}`"
            class="m-0"
            target="_blank"
          >
            {{ item.name }}
          </a>
        </div>
      </template>

      <template #item.departments="{ item }">
        <div v-for="(department, index) in item.departments" :key="department.code">
          <span class="green-bold-text">{{ department.name }}</span> - {{ department.role }}
          <div v-if="index !== item.departments.length - 1"></div>
        </div>
        <div v-if="item.canEditDegreeProgress || item.canReadDegreeProgress" class="gray-text">
          <span class="bold-text">Degree Progress - </span>
          <span v-if="item.canEditDegreeProgress && item.canReadDegreeProgress"> read/write</span>
          <span v-if="!(item.canEditDegreeProgress && item.canReadDegreeProgress) && item.canReadDegreeProgress"> read</span>
          <span v-if="item.automateDegreeProgressPermission"> (automated)</span>
        </div>
      </template>

      <template #item.deletedAt="{ item }">
        <div v-for="(status, index) in getUserStatuses(item)" :key="index">
          {{ status }}
        </div>
      </template>

      <template #item.lastLogin="{ item }">
        <span :id="`user-last-login-${item.uid}`">
          <span v-if="item.lastLogin">{{ DateTime.fromISO(item.lastLogin).toFormat('DD') }}</span>
          <!-- <span v-if="item.lastLogin">{{ moment(item.lastLogin).format('MMM D, YYYY') }}</span> -->
          <span v-if="!item.lastLogin">&mdash;</span>
        </span>
      </template>

      <template #item.campusEmail="{ item }">
        <a
          :aria-label="`Send email to ${item.name}`"
          :href="`mailto:${item.campusEmail}`"
          target="_blank"
        >
          <v-icon :icon="mdiEmail"></v-icon>
          <span class="sr-only"> (will open new browser tab)</span>
        </a>

        <v-btn
          v-if="canBecome(item)"
          :id="'become-' + item.uid"
          variant="plain"
          @click="become(item.uid)"
        >
          <v-icon color="primary" :icon="mdiLoginVariant"></v-icon>
          <span class="sr-only">Log in as {{ item.name }}</span>
        </v-btn>
      </template>
      <template #bottom></template>
    </v-data-table-server>
  </div>
</template>

<script setup>
import {mdiEmail} from '@mdi/js'
import {mdiLoginVariant} from '@mdi/js'
import {ref} from 'vue'
</script>

<script>
import Context from '@/mixins/Context'
import EditUserProfileModal from '@/components/admin/EditUserProfileModal'
import Autocomplete from '@/components/util/Autocomplete.vue'
import Util from '@/mixins/Util'
import {alertScreenReader} from '@/lib/utils'
import {becomeUser, getAdminUsers, getUserByUid, getUsers, userAutocomplete} from '@/api/user'
import {getBoaUserRoles} from '@/berkeley'
import {DateTime} from 'luxon'

export default {
  name: 'Users',
  components: {EditUserProfileModal, Autocomplete},
  mixins: [Context, Util],
  props: {
    departments: {
      required: true,
      type: Array
    },
    refresh: {
      required: false,
      type: Boolean
    }
  },
  data: () => ({
    expanded: [],
    currentPage: 1,
    itemsPerPage: 10,
    filterBy: {
      deptCode: 'QCADV',
      role: null,
      searchPhrase: '',
      status: null
    },
    filterType: 'search',
    isBusy: false,
    sortBy: 'lastName',
    sortDesc: false,
    totalUserCount: 0,
    userSelection: undefined,
    departmentSelectionList: [],
    users: [],
    allUsersCache: [],
    items: ref([]),
    filterTypeOptions: [
      {
        name: 'Search',
        value: 'search'
      },
      {
        name: 'BOA Admins',
        value: 'admins'
      },
      {
        name: 'Filter',
        value: 'filter'
      }
    ],
    userPermissionOptions: [
      {
        name: 'All',
        value: null
      },
      {
        name: 'Advisors',
        value: 'advisor'
      },
      {
        name: 'No Canvas Data',
        value: 'noCanvasDataAccess'
      },
      {
        name: 'No Notes or Appointments',
        value: 'noAdvisingDataAccess'
      },
      {
        name: 'Directors',
        value: 'director'
      }
    ],
    userStatusOptions: [
      {
        name: 'All',
        value: null
      },
      {
        name: 'Active',
        value: 'active'
      },
      {
        name: 'Deleted',
        value: 'deleted'
      },
      {
        name: 'Blocked',
        value: 'blocked'
      }
    ],
    tableHeaders: [
      {
        title: '',
        key: 'data-table-expand',
        align: 'start',
        sortable: false
      },
      {
        title: 'UID',
        key: 'uid',
        align: 'start',
        sortable: false,
        headerProps: {
          class: ['header-text-styling']
        },
      },
      {
        title: '',
        key: 'edit',
        align: 'end',
        sortable: false,
        cellProps: {
          class: 'purple-background'
        },
      },
      {
        title: 'Last Name',
        key: 'lastName',
        align: 'start',
        sortable: true,
        headerProps: {
          class: ['header-text-styling']
        },
        cellProps: {
          class: 'purple-background'
        },
      },
      {
        title: 'Departments',
        key: 'departments',
        align: 'start',
        sortable: false,
        headerProps: {
          class: ['header-text-styling']
        },
      },
      {
        title: 'Status',
        key: 'deletedAt',
        align: 'start',
        sortable: false,
        headerProps: {
          class: ['header-text-styling']
        },
      },
      {
        title: 'Last Login',
        key: 'lastLogin',
        align: 'start',
        sortable: true,
        headerProps: {
          class: ['header-text-styling']
        },
        cellProps: {
          class: 'light-green-background'
        }
      },
      {
        title: 'Email',
        key: 'campusEmail',
        align: 'start',
        sortable: false,
        headerProps: {
          class: ['header-text-styling']
        },
      }
    ]
  }),
  watch: {
    refresh(value) {
      if (value) {
        this.refreshUsers()
      }
    },
    userSelection(newVal) {
      if (newVal) {
        this.refreshUsers()
      }
    }
  },
  created() {
    this.departmentSelectionList = [{
      id: -1, code: null, name: 'All'
    }, ...this.departments]

  },
  mounted() {
    this.usersProvider()
  },
  methods: {
    handleSort(sortBy) {
      this.sortBy = sortBy[0].key
      this.sortDesc = sortBy[0].order === 'asc' ? false : true
      this.usersProvider() // Method to fetch users with new sorting parameters
    },
    clickColumn(slotData) {
      const indexExpanded = this.expanded.findIndex(i => i === slotData)
      if (indexExpanded > -1) {
        this.expanded.splice(indexExpanded, 1)
      } else {
        this.expanded.push(slotData)
      }
    },
    afterUpdateUser(profile) {
      alertScreenReader(`${profile.name} profile updated.`)
      if (this.filterType === 'search') {
        this.userSelection = profile.uid
      }
      this.refreshUsers()
    },
    autocompleteUsers(q) {
      return userAutocomplete(q).then(results => this._orderBy(results, 'label'))
    },
    become(uid) {
      becomeUser(uid).then(() => window.location.href = '/')
    },
    canBecome(user) {
      const isNotMe = user.uid !== this.currentUser.uid
      const expiredOrInactive = user.isExpiredPerLdap || user.deletedAt || user.isBlocked
      const hasAnyRole = user?.isAdmin || this._find(user.departments, (dept) => !this._isNil(dept.role))
      return this.config.devAuthEnabled && isNotMe && !expiredOrInactive && hasAnyRole
    },
    getBoaUserRoles,
    getUserStatuses(user) {
      const statuses = user.deletedAt ? ['Deleted'] : ['Active']
      if (user.isBlocked) {
        statuses.push('Blocked')
      }
      if (user.isExpiredPerLdap) {
        statuses.push('Expired, according to CalNet.')
      }
      return statuses
    },
    openEditUserModal(user) {
      user.showEditUserModal = true
    },
    quickLink(role, deptCode=null) {
      this.filterType = 'filter'
      this.filterBy = {
        deptCode: deptCode,
        role: role,
        searchPhrase: '',
        status: 'active'
      }
      this.refreshUsers()
    },
    refreshUsers() {
      this.usersProvider()
    },
    userSelected(selectedUser) {
      this.userSelection = selectedUser
    },
    usersProvider() {
      let promise = undefined
      switch(this.filterType) {
      case 'admins':
        this.totalUserCount = undefined
        promise = getAdminUsers(this.sortBy, this.sortDesc, false).then(data => {
          this.totalUserCount = data.totalUserCount
          this.users = data.users
          return data.users
        })
        break
      case 'filter':
        this.totalUserCount = undefined
        promise = getUsers(
          this._isNil(this.filterBy.status) ? null : this.filterBy.status === 'blocked',
          this._isNil(this.filterBy.status) ? null : this.filterBy.status === 'deleted',
          this.filterBy.deptCode,
          this.filterBy.role,
          this.sortBy,
          this.sortDesc
        ).then(data => {
          this.totalUserCount = data.totalUserCount
          this.users = data.users
          return data.users
        })
        break
      case 'search':
        this.totalUserCount = 0
        this.users = []
        if (this.userSelection) {
          promise = getUserByUid(this.userSelection, false).then(data => {
            this.totalUserCount = 1
            this.userSelection = undefined
            this.users = [data]
            return [data]
          })
        } else {
          promise = new Promise(resolve => resolve([]))
        }
        this.putFocusNextTick('search-user-input')
        break
      default:
        promise = new Promise(resolve => resolve([]))
      }
      return promise
    },
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
  padding-top: 6px !important;
  width: 25px;
}
.column-toggle-details-button {
  color: #337ab7;
  height: 15px;
  line-height: 1;
  padding: 0 !important;
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
.color-gray-100 {
  background-color: #f9f9f9;
}
.dark-gray-background {
  background-color: #e0dede;
}
.purple-background {
  background-color: #9bcbfb;
  color: #377eb6;
  font-weight: 900;
}
.light-green-background {
  background-color: #bee5eb;
  font-weight: 900;
}
.header-text-styling {
  font-weight: 900;
  font-size: 16px;
}
.custom-select-container {
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
}

.custom-select-container label {
  font-size: 16px;
  margin-bottom: 8px;
  color: #6b6b6b; /* Matching Vuetify's label color */
}

.custom-select {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  background-color: white;
  border: 1px solid #ced4da;
  border-radius: 4px;
  padding: 8px 16px;
  font-size: 16px;
  color: #495057;
  box-shadow: none;
  transition: border-color 0.3s, box-shadow 0.3s;
}

.custom-select:focus {
  border-color: #3f51b5; /* Matching Vuetify's focus color */
  outline: none;
  box-shadow: 0 0 0 2px rgba(63, 81, 181, 0.25); /* Matching Vuetify's focus shadow */
}

.custom-select:disabled {
  background-color: #e9ecef;
  color: #6c757d;
}

.gray-text {
  color: gray;
}

.green-bold-text {
  color: green;
  font-weight: 900;
}

.bold-text {
  font-weight: 900;
}

.v-table tbody tr:nth-child(odd) {
      background-color: rgba(0, 0, 0, .05);
}

.v-table tbody tr:nth-child(even) {
      background-color: white;
}

.v-table tbody tr {
  padding: 4px 0px;
}

.v-data-table__td--expanded-row {
  color: #337ab7;
}
</style>
