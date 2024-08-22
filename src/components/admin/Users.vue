<template>
  <div>
    <v-container class="pb-0 pl-0 pr-6" fluid>
      <v-row align-v="center" class="pt-2" no-gutters>
        <v-col cols="3">
          <div class="mr-3">
            <select
              id="user-filter-options"
              v-model="filterType"
              class="select-menu w-100"
              :disabled="isBusy"
            >
              <option
                v-for="option in filterTypeOptions"
                :key="option.value"
                :value="option.value"
                @select="refreshUsers"
              >
                {{ option.name }}
              </option>
            </select>
          </div>
        </v-col>
        <v-col cols="9">
          <div v-if="filterType === 'search'">
            <span id="user-search-input" class="sr-only">Search for user. Expect auto-suggest as you type name or UID.</span>
            <Autocomplete
              id="search-user-input"
              v-model="userSelection"
              :compact="true"
              :disabled="isBusy"
              :fetch="userAutocomplete"
              option-label-key="label"
              option-value-key="uid"
              placeholder="Enter name..."
              :show-no-data="true"
              @user-selected="userSelected"
            />
          </div>
          <div v-if="filterType === 'filter'" class="d-flex">
            <div class="pr-2">
              <select
                id="department-select-list"
                v-model="filterBy.deptCode"
                class="select-menu"
                :disabled="isBusy"
                @update:model-value="refreshUsers"
              >
                <option
                  v-for="option in departmentSelectionList"
                  :id="`department-option-${option.code}`"
                  :key="option.code"
                  :value="option.code"
                >
                  {{ option.name }}
                </option>
              </select>
            </div>
            <div class="pr-2">
              <select
                id="user-permission-options"
                v-model="filterBy.role"
                class="select-menu"
                :disabled="isBusy"
                @update:model-value="refreshUsers"
              >
                <option
                  v-for="option in userPermissionOptions"
                  :id="`user-permission-${option.value}`"
                  :key="option.value"
                  :value="option.value"
                >
                  {{ option.name }}
                </option>
              </select>
            </div>
            <div class="pr-2">
              <select
                id="user-status-options"
                v-model="filterBy.status"
                class="select-menu"
                :disabled="isBusy"
                @update:model-value="refreshUsers"
              >
                <option
                  v-for="option in userStatusOptions"
                  :id="`user-permission-${option.value}`"
                  :key="option.value"
                  :value="option.value"
                >
                  {{ option.name }}
                </option>
              </select>
            </div>
          </div>
        </v-col>
      </v-row>
      <v-row align="center">
        <v-col class="align-center d-flex pl-4" cols="10">
          <div class="quick-links-label">
            Quick links:
          </div>
          <div>
            <v-btn
              id="quick-link-directors"
              class="font-size-16 px-0"
              color="primary"
              :disabled="isBusy"
              min-width="60"
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
              class="font-size-16 px-0"
              color="primary"
              :disabled="isBusy"
              exact
              min-width="220"
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
              class="font-size-16 px-0"
              color="primary"
              exact
              min-width="140"
              variant="text"
              @click="quickLink('advisor', 'QCADV')"
            >
              L&amp;S Advisors
            </v-btn>
          </div>
        </v-col>
        <v-col>
          <div
            v-if="totalUserCount > 0"
            class="float-right font-size-16 font-weight-medium pr-4 text-grey"
          >
            {{ pluralize('user', totalUserCount) }}
          </div>
        </v-col>
      </v-row>
    </v-container>
    <div class="mt-3">
      <v-data-table-server
        v-model:expanded="expanded"
        v-model:items-per-page="itemsPerPage"
        :cell-props="data => {
          const padding = ['becomeUser', 'data-table-expand', 'edit'].includes(data.column.key) ? 'px-0' : ''
          return {
            class: `${padding}`,
            id: normalizeId(`td-user-${data.item.uid}-column-${data.column.key}`)
          }
        }"
        :headers="tableHeaders"
        :header-props="{class: 'font-size-14 py-3 text-no-wrap'}"
        :hide-default-footer="true"
        hide-no-data
        :items-length="totalUserCount || 0"
        :items-per-page="0"
        :items="users"
        :loading="totalUserCount === undefined"
        disable-pagination
        item-value="uid"
        loading-text="Fetching users..."
        :row-props="data => {
          const bgColor = data.index % 2 === 0 ? 'bg-grey-lighten-4' : ''
          return {
            class: `${bgColor}`,
            id: `tr-user-${data.item.uid}`
          }
        }"
        show-expand
        @update:sort-by="handleSort"
        @update:sort-desc="handleSort"
      >
        <template #item.uid="{ item }">
          {{ item.uid }}
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
            :after-cancel="afterCancelUpdateUser"
            :after-update-user="afterUpdateUser"
            :departments="departments"
            :profile="item"
          />
        </template>

        <template #item.lastName="{ item }">
          <div class="name-container">
            <div class="icons">
              <span v-if="!item.canAccessCanvasData">
                <span class="c-letter">C</span>
                <span class="slash">\</span>
              </span>
              <span v-if="!item.canAccessAdvisingData" class="advising-data">
                <span class="slash-2">\</span>
                <v-icon :icon="mdiNoteOutline" size="small" />
              </span>
            </div>
            <div v-if="!item.name" class="name">
              <span class="faint-text text-body-2">(Name unavailable)</span>
            </div>
            <div v-if="item.name" class="name">
              <a
                :id="`directory-link-${item.uid}`"
                :aria-label="`Go to UC Berkeley Directory page of ${item.name}`"
                :href="`https://www.berkeley.edu/directory/results?search-term=${item.name}`"
                target="_blank"
              >
                {{ item.name }}
              </a>
            </div>
          </div>
        </template>

        <template #item.departments="{ item }">
          <div class="row-padding">
            <div v-for="(department, index) in item.departments" :key="department.code">
              <span class="green-bold-text text-body-2">{{ department.name }} - {{ department.role }}</span>
              <div v-if="index !== item.departments.length - 1"></div>
            </div>
            <div v-if="item.canEditDegreeProgress || item.canReadDegreeProgress" class="gray-text">
              <span class="bold-text text-body-2">Degree Progress - </span>
              <span v-if="item.canEditDegreeProgress && item.canReadDegreeProgress" class="text-body-2"> read/write</span>
              <span v-if="!(item.canEditDegreeProgress && item.canReadDegreeProgress) && item.canReadDegreeProgress" class="text-body-2"> read</span>
              <span v-if="item.automateDegreeProgressPermission" class="text-body-2"> (automated)</span>
            </div>
          </div>
        </template>

        <template #item.deletedAt="{ item }">
          <div v-for="(status, index) in getUserStatuses(item)" :key="index">
            {{ status }}
          </div>
        </template>

        <template #item.lastLogin="{ item }">
          <span :id="`user-last-login-${item.uid}`">
            <span v-if="item.lastLogin" class="text-body-2">{{ DateTime.fromISO(item.lastLogin).toFormat('DD') }}</span>
            <span v-if="!item.lastLogin">&mdash;</span>
          </span>
        </template>

        <template #item.campusEmail="{ item }">
          <div class="text-center">
            <a
              :aria-label="`Send email to ${item.name}`"
              :href="`mailto:${item.campusEmail}`"
              target="_blank"
            >
              <v-icon :icon="mdiEmail" />
              <span class="sr-only"> (will open new browser tab)</span>
            </a>
          </div>
        </template>
        <template #item.becomeUser="{ item }">
          <v-btn
            v-if="canBecome(item)"
            :id="`become-${item.uid}`"
            :aria-label="`Log in as ${item.name}`"
            class="text-primary"
            flat
            :icon="mdiLoginVariant"
            size="sm"
            @click="() => become(item.uid)"
          />
        </template>
        <template #bottom></template>
      </v-data-table-server>
    </div>
  </div>
</template>

<script setup>
import {get} from 'lodash'
import {mdiEmail} from '@mdi/js'
import {mdiLoginVariant} from '@mdi/js'
import {normalizeId} from '@/lib/utils'
import {mdiNoteOutline} from '@mdi/js'
import {ref} from 'vue'
</script>

<script>
import Context from '@/mixins/Context'
import EditUserProfileModal from '@/components/admin/EditUserProfileModal'
import Autocomplete from '@/components/util/Autocomplete.vue'
import Util from '@/mixins/Util'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
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
        sortable: false
      },
      {
        title: 'UID',
        key: 'uid',
        sortable: false,
        align: 'start',
        headerProps: {
          class: ['header-text-styling']
        }
      },
      {
        title: '',
        key: 'edit',
        align: 'end',
        sortable: false,
        headerProps: {
          class: ['header-text-styling']
        },
        cellProps: {
          class: ['manifest-column-name', 'purple-background']
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
          class: ['manifest-column-name', 'purple-background'],
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
        cellProps: {
          class: 'manifest-column-last-login'
        },
        headerProps: {
          class: ['header-text-styling']
        },
      },
      {
        title: 'Email',
        key: 'campusEmail',
        align: 'start',
        sortable: false,
      },
      {
        title: '',
        key: 'becomeUser',
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
      if (sortBy.length) {
        this.sortBy = sortBy[0].key
        this.sortDesc = sortBy[0].order === 'asc' ? false : true
        this.usersProvider() // Method to fetch users with new sorting parameters
      }
    },
    afterCancelUpdateUser(profile) {
      alertScreenReader('Canceled')
      putFocusNextTick(get(profile, 'uid') ? `edit-${profile.uid}` : 'add-new-user-btn')
    },
    afterUpdateUser(profile) {
      alertScreenReader(`${profile.name} profile updated.`)
      if (this.filterType === 'search') {
        this.userSelection = profile.uid
      }
      this.refreshUsers()
      putFocusNextTick(get(profile, 'uid') ? `edit-${profile.uid}` : 'add-new-user-btn')
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
.manifest-column-name {
  background-color: #9bcbfb;
  color: #377eb6;
  font-weight: 900;
}
.manifest-column-last-login {
  background-color: #bee5eb;
  font-weight: 900;
},
.on-top-of-table {
  z-index: 1000;
  position: relative;
  top: -17px;
},
.table-wrapper {
  position: relative;
  top: -44px;
}
</style>

<style scoped>
.quick-links-label {
  font-size: 18px;
  font-weight: 600;
  padding-bottom: 2px;
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
  font-size: 14px;
  position: relative;
  top: 16px;
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
  padding: 12px 0px;
}
.v-data-table__td--expanded-row {
  color: #337ab7;
}
.row-padding {
  padding: 12px !important;
}
:deep(.v-table > .v-table__wrapper > table > thead > tr > th) {
  height: 40px !important;
}
.c-letter {
  position: relative;
  top: 1px;
  left: 1px;
}
.slash {
  position: relative;
  top: 4px;
  left: -8px;
  font-size: 22px;
  color: red;
}
.slash-2 {
  position: relative;
  top: 4px;
  left: 12px;
  font-size: 22px;
  color: red;
  z-index: 10000;
}
.advising-data {
  position: relative;
  left: -8px;
}
.name-container {
  position: relative;
  top: -1px;
}
.icons {
  position: relative;
  top: -1px;
  display: inline-block;
}
.name {
  position: relative;
  display: inline-block;
}
:deep(.v-table > .v-table__wrapper > table > thead > tr > th) {
  height: 0px !important;
}
</style>
