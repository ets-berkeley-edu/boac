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
              :disabled="isFetching"
            >
              <option
                v-for="option in [
                  {name: 'Search', value: 'search'},
                  {name: 'BOA Admins', value: 'admins'},
                  {name: 'Filter', value: 'filter'}
                ]"
                :key="option.value"
                :value="option.value"
              >
                {{ option.name }}
              </option>
            </select>
          </div>
        </v-col>
        <v-col cols="5">
          <div v-if="filterType === 'search'">
            <span id="user-search-input" class="sr-only">Search for user. Expect auto-suggest as you type name or UID.</span>
            <v-autocomplete
              id="search-user-input"
              autocomplete="off"
              base-color="black"
              :class="{'demo-mode-blur': contextStore.currentUser.inDemoMode}"
              color="grey"
              density="compact"
              hide-details
              :hide-no-data="size(autocompleteInput) < 3 || isFetching || isSuggesting || suggestedUsers.length"
              :items="suggestedUsers"
              label="Enter name..."
              :maxlength="72"
              :menu-icon="null"
              :model-value="userSelection"
              no-data-text="No match found"
              return-object
              variant="outlined"
              @update:model-value="onUpdateAutocompleteModel"
              @update:search="onUpdateSearch"
            >
              <template #append-inner>
                <v-progress-circular
                  v-if="isSuggesting"
                  color="pale-blue"
                  indeterminate
                  :size="16"
                  :width="3"
                />
              </template>
            </v-autocomplete>
          </div>
          <div v-if="filterType === 'filter'" class="d-flex">
            <div class="pr-2">
              <select
                id="department-select-list"
                v-model="filterBy.deptCode"
                class="select-menu"
                :disabled="isFetching"
                @update:model-value="fetchUsers"
              >
                <option
                  v-for="option in [{id: -1, code: null, name: 'All'}, ...departments]"
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
                :disabled="isFetching"
                @update:model-value="fetchUsers"
              >
                <option
                  v-for="option in [
                    {name: 'All', value: null},
                    {name: 'Advisors', value: 'advisor'},
                    {name: 'No Canvas Data', value: 'noCanvasDataAccess'},
                    {name: 'No Notes or Appointments', value: 'noAdvisingDataAccess'},
                    {name: 'Directors', value: 'director'}
                  ]"
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
                :disabled="isFetching"
                @update:model-value="fetchUsers"
              >
                <option
                  v-for="option in [
                    {name: 'All', value: null},
                    {name: 'Active', value: 'active'},
                    {name: 'Deleted', value: 'deleted'},
                    {name: 'Blocked', value: 'blocked'}
                  ]"
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
        :headers="[
          {title: '', key: 'data-table-expand', sortable: false},
          {title: 'UID', key: 'uid', sortable: false, align: 'start', headerProps: {class: ['header-text-styling']}},
          {title: '', key: 'edit', align: 'end', sortable: false, headerProps: {class: ['header-text-styling']}, cellProps: {class: ['manifest-column-name', 'purple-background']}},
          {title: 'Last Name', key: 'lastName', align: 'start', sortable: true, headerProps: {class: ['header-text-styling']}, cellProps: {class: ['manifest-column-name', 'purple-background']}},
          {title: 'Departments', key: 'departments', align: 'start', sortable: false, headerProps: {class: ['header-text-styling']}},
          {title: 'Status', key: 'deletedAt', align: 'start', sortable: false, headerProps: {class: ['header-text-styling']}},
          {title: 'Last Login', key: 'lastLogin', align: 'start', sortable: true, cellProps: {class: 'manifest-column-last-login'}, headerProps: {class: ['header-text-styling']}},
          {title: 'Email', key: 'campusEmail', align: 'start', sortable: false},
          {title: '', key: 'becomeUser', sortable: false, headerProps: {class: ['header-text-styling']}}
        ]"
        :header-props="{class: 'font-size-14 py-3 text-no-wrap'}"
        :hide-default-footer="true"
        :items-length="totalUserCount || 0"
        :items-per-page="0"
        :items="users"
        :loading="isFetching"
        disable-pagination
        item-value="uid"
        loading-text="Searching..."
        :no-data-text="isFetching || isNil(totalUserCount) ? '' : 'No users'"
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
            :after-update-user="afterEditUserProfile"
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
              <span class="font-weight-bold text-body-2 text-green">{{ department.name }} - {{ department.role }}</span>
              <div v-if="index !== item.departments.length - 1"></div>
            </div>
            <div v-if="item.canEditDegreeProgress || item.canReadDegreeProgress" class="text-grey">
              <span class="font-weight-bold text-body-2">Degree Progress - </span>
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
import EditUserProfileModal from '@/components/admin/EditUserProfileModal'
import {alertScreenReader, pluralize, putFocusNextTick} from '@/lib/utils'
import {becomeUser, getAdminUsers, getUserByUid, getUsers, userAutocomplete} from '@/api/user'
import {DateTime} from 'luxon'
import {debounce, find, get, isNil, map, size, trim} from 'lodash'
import {escapeForRegExp, normalizeId} from '@/lib/utils'
import {mdiEmail} from '@mdi/js'
import {mdiLoginVariant, mdiNoteOutline} from '@mdi/js'
import {onMounted, ref, watch} from 'vue'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  departments: {
    required: true,
    type: Array
  },
  refresh: {
    required: false,
    type: Boolean
  }
})

const contextStore = useContextStore()

const autocompleteInput = ref(undefined)
const expanded = ref([])
const itemsPerPage = 10
const filterBy = ref({
  deptCode: 'QCADV',
  role: null,
  searchPhrase: '',
  status: null
})
const filterType = ref('search')
const isFetching = ref(false)
const isSuggesting = ref(false)
const sortBy = ref('lastName')
const sortDesc = ref(false)
const suggestedUsers = ref([])
const totalUserCount = ref(undefined)
const userSelection = ref(undefined)
const users = ref([])

watch(filterType, () => {
  fetchUsers()
})

watch(() => props.refresh, value => {
  if (value) {
    fetchUsers()
  }
})

onMounted(() => {
  fetchUsers()
})

const handleSort = sortBy => {
  if (sortBy.length) {
    sortBy.value = sortBy[0].key
    sortDesc.value = sortBy[0].order !== 'asc'
    fetchUsers() // Method to fetch users with new sorting parameters
  }
}

const afterCancelUpdateUser = profile => {
  alertScreenReader('Canceled')
  putFocusNextTick(get(profile, 'uid') ? `edit-${profile.uid}` : 'add-new-user-btn')
}

const afterEditUserProfile = profile => {
  alertScreenReader(`${profile.name} profile updated.`)
  if (filterType.value === 'search') {
    userSelection.value = profile.uid
  }
  fetchUsers()
  putFocusNextTick(get(profile, 'uid') ? `edit-${profile.uid}` : 'add-new-user-btn')
}

const become = uid => {
  becomeUser(uid).then(() => window.location.href = '/')
}

const canBecome = user => {
  const isNotMe = user.uid !== contextStore.currentUser.uid
  const expiredOrInactive = user.isExpiredPerLdap || user.deletedAt || user.isBlocked
  const hasAnyRole = user?.isAdmin || find(user.departments, (dept) => !isNil(dept.role))
  return contextStore.config.devAuthEnabled && isNotMe && !expiredOrInactive && hasAnyRole
}

const getUserStatuses = user => {
  const statuses = user.deletedAt ? ['Deleted'] : ['Active']
  if (user.isBlocked) {
    statuses.push('Blocked')
  }
  if (user.isExpiredPerLdap) {
    statuses.push('Expired, according to CalNet.')
  }
  return statuses
}

const onUpdateAutocompleteModel = user => {
  userSelection.value = user
  fetchUsers()
}

const onUpdateSearch = debounce(query => {
  autocompleteInput.value = query && trim(escapeForRegExp(query).replace(/[^\w ]+/g, ''))
  if (size(autocompleteInput.value) > 1) {
    isSuggesting.value = true
    userAutocomplete(autocompleteInput.value, new AbortController()).then(results => {
      suggestedUsers.value = map(results, result => ({title: result.label, value: result}))
      isSuggesting.value = false
    })
  }
}, 500)

const quickLink = (role, deptCode=null) => {
  filterType.value = 'filter'
  filterBy.value = {
    deptCode: deptCode,
    role: role,
    searchPhrase: '',
    status: 'active'
  }
  fetchUsers()
}

const fetchUsers = () => {
  const isValidSelection = (filterType.value !== 'search') || get(userSelection.value, 'value.uid')
  if (isValidSelection) {
    isFetching.value = true
    totalUserCount.value = 0
    users.value = []
    switch(filterType.value) {
    case 'admins':
      getAdminUsers(sortBy.value, sortDesc.value, false).then(data => {
        users.value = data.users
        totalUserCount.value = data.totalUserCount
        isFetching.value = false
      })
      break
    case 'filter':
      getUsers(
        isNil(filterBy.value.status) ? null : filterBy.value.status === 'blocked',
        isNil(filterBy.value.status) ? null : filterBy.value.status === 'deleted',
        filterBy.value.deptCode,
        filterBy.value.role,
        sortBy.value,
        sortDesc.value
      ).then(data => {
        users.value = data.users
        totalUserCount.value = data.totalUserCount
        isFetching.value = false
      })
      break
    case 'search':
      getUserByUid(userSelection.value.value.uid, false).then(data => {
        users.value = [data]
        totalUserCount.value = 1
        isFetching.value = false
        userSelection.value = null
      })
      putFocusNextTick('search-user-input')
      break
    }
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
}
.on-top-of-table {
  z-index: 1000;
  position: relative;
  top: -17px;
}
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
  z-index: 100;
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
