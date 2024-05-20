<template>
  <div>
    <v-container fluid class="mb-2">
      <v-row align-v="center" no-gutters>
        <v-col cols="2" class="pr-2">
          <v-select
            id="user-filter-options"
            v-model="filterType"
            :disabled="isBusy"
            :items="filterTypeOptions"
            item-title="name"
            item-value="value"
            variant="outlined"
            density="compact"
            style="font-size: 16px;"
            @update:modelValue="refreshUsers"
          >
          </v-select>
        </v-col>
        <v-col v-if="filterType === 'search'" cols="10">
          <span id="user-search-input" class="sr-only">Search for user. Expect auto-suggest as you type name or UID.</span>
          <Autocomplete
            id="search-options-note-filters-author"
            v-model="userSelection"
            :compact="true"
            :disabled="isBusy"
            :fetch="userAutocomplete"
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
                @update:modelValue="refreshUsers"
              >
                <!-- <option :value="null">All</option>
                <option
                  v-for="department in departments"
                  :key="department.code"
                  :value="department.code"
                >
                  {{ department.name }}
                </option> -->
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
                @update:modelValue="refreshUsers"
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
                @update:modelValue="refreshUsers"
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
          class="pl-2 pr-2 pb-3"
          variant="link"
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
          class="pl-2 pr-2 pb-3"
          variant="link"
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
          class="pl-2 pr-2 pb-3"
          variant="link"
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

      <template #item.name="{ item }">
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
          {{ department.name }} - {{ department.role }}
          <div v-if="index !== item.departments.length - 1"></div>
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
          <v-icon :icon="mdiLoginVariant"></v-icon>
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
    sortDescending: false,
    totalUserCount: 0,
    userSelection: undefined,
    departmentSelectionList: [],
    users: [],
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
        align: 'start'
      },
      {
        title: 'UID',
        key: 'uid',
        align: 'start'
      },
      {
        title: '',
        key: 'edit',
        align: 'end'
      },
      {
        title: 'Name',
        key: 'name',
        align: 'start'
      },
      {
        title: 'Departments',
        key: 'departments',
        align: 'start'
      },
      {
        title: 'Status',
        key: 'deletedAt',
        align: 'start'
      },
      {
        title: 'Last Login',
        key: 'lastLogin',
        align: 'start'
      },
      {
        title: 'Email',
        key: 'campusEmail',
        align: 'start'
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
        this.onUpdateSearch()
      }
    }
  },
  created() {
    // console.log('this.departments', this.departments)
    this.departmentSelectionList = [{
      id: -1, code: null, name: 'All'
    }, ...this.departments]

  },
  mounted() {
    this.usersProvider()
  },
  methods: {
    clickColumn(slotData) {
      const indexExpanded = this.expanded.findIndex(i => i === slotData)
      if (indexExpanded > -1) {
        this.expanded.splice(indexExpanded, 1)
      } else {
        this.expanded.push(slotData)
      }
    },
    afterUpdateUser(profile) {
      this.alertScreenReader(`${profile.name} profile updated.`)
      if (this.filterType === 'search') {
        this.userSelection = profile
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
        promise = getAdminUsers(this.sortBy, this.sortDescending, false).then(data => {
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
          this.sortDescending
        ).then(data => {
          this.totalUserCount = data.totalUserCount
          this.users = data.users
          return data.users
        })
        break
      case 'search':
        this.totalUserCount = 0
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
</style>
