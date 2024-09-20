<template>
  <div>
    <v-container class="pb-0 pl-0 pr-6" fluid>
      <v-row align-v="center" class="pt-2" no-gutters>
        <v-col cols="3">
          <div class="pr-3">
            <select
              id="user-filter-options"
              v-model="filterType"
              class="select-menu w-100"
              :disabled="isBecoming || isFetching"
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
        <v-col cols="9">
          <div v-if="filterType === 'search'">
            <span id="user-search-input" class="sr-only">Search for user. Expect auto-suggest as you type name or UID.</span>
            <v-autocomplete
              id="search-user-input"
              autocomplete="off"
              base-color="black"
              :class="{'demo-mode-blur': contextStore.currentUser.inDemoMode}"
              density="compact"
              :disabled="isBecoming"
              hide-details
              :hide-no-data="!!(size(autocompleteInput) < 3 || isFetching || isSuggesting || suggestedUsers.length)"
              :items="suggestedUsers"
              label="Enter name or UID"
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
                  color="primary"
                  indeterminate
                  :size="18"
                  :width="3"
                />
              </template>
            </v-autocomplete>
          </div>
          <div v-if="filterType === 'filter'" class="d-flex flex-wrap">
            <div class="pr-2">
              <select
                id="department-select-list"
                v-model="filterBy.deptCode"
                aria-label="department"
                class="select-menu mb-1"
                :disabled="isBecoming || isFetching"
                @update:model-value="fetchUsers('user-permission-options')"
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
                aria-label="user permissions"
                class="select-menu mb-1"
                :disabled="isBecoming || isFetching"
                @update:model-value="fetchUsers('user-status-options')"
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
                aria-label="user status"
                class="select-menu"
                :disabled="isBecoming || isFetching"
                @update:model-value="fetchUsers('user-status-options')"
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
              id="quick-link-ce3-advisors"
              class="font-size-16 px-0"
              color="primary"
              min-width="60"
              variant="text"
              @click="quickLink('advisor', 'ZCEEE', 'quick-link-ce3-advisors')"
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
              @click="quickLink('advisor', 'COENG', 'quick-link-coe-advisors')"
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
              @click="quickLink('advisor', 'QCADV', 'quick-link-qcadv-advisors')"
            >
              L&amp;S Advisors
            </v-btn>
          </div>
        </v-col>
        <v-col>
          <div
            v-if="totalUserCount > 0"
            class="float-right font-size-16 font-weight-medium pr-4 text-medium-emphasis"
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
        class="responsive-data-table v-table-hidden-row-override"
        :headers="[
          {title: '', key: 'data-table-expand', sortable: false, width: 40},
          {title: 'UID', key: 'uid', sortable: false, align: 'start'},
          {title: '', key: 'edit', align: 'end', ariaLabel: 'edit user', sortable: false, cellProps: {class: ['manifest-column-name']}},
          {title: 'Name', key: 'lastName', align: 'start', sortable: true, cellProps: {class: ['manifest-column-name']}},
          {title: 'Departments', key: 'departments', align: 'start', headerProps: {class: 'pl-2'}, sortable: false},
          {title: 'Status', key: 'deletedAt', align: 'start', sortable: false},
          {title: 'Last Login', key: 'lastLogin', align: 'start', sortable: true, cellProps: {class: 'manifest-column-last-login'}},
          {title: 'Email', key: 'campusEmail', align: 'start', sortable: false},
          {title: '', key: 'becomeUser', sortable: false}
        ]"
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
          const bgColor = data.index % 2 === 0 ? 'bg-surface-light' : ''
          return {
            class: `${bgColor}`,
            id: `tr-user-${data.item.uid}`
          }
        }"
        show-expand
        @update:sort-by="handleSort"
      >
        <template #headers="{columns, isSorted, toggleSort, getSortIcon}">
          <tr>
            <th
              v-for="column in columns"
              :key="column.key"
              :aria-label="column.ariaLabel || column.title"
              :aria-sort="isSorted(column) ? `${sortBy.order}ending` : null"
              class="py-3 text-no-wrap"
              :width="column.width"
            >
              <template v-if="column.sortable">
                <v-btn
                  :id="`admits-sort-by-${column.key}-btn`"
                  :append-icon="getSortIcon(column)"
                  :aria-label="`Sort by ${column.ariaLabel || column.title} ${isSorted(column) && sortBy.order === 'asc' ? 'descending' : 'ascending'}`"
                  class="font-size-14 font-weight-bold height-unset min-width-unset pa-1 text-uppercase v-table-sort-btn-override"
                  :class="{'align-start': column.align === 'start', 'icon-visible': isSorted(column)}"
                  color="body"
                  density="compact"
                  variant="plain"
                  @click="() => toggleSort(column)"
                >
                  <span class="text-left">{{ column.title }}</span>
                </v-btn>
              </template>
              <template v-else>
                <div
                  :aria-hidden="!!column.ariaLabel"
                  class="not-sortable font-size-14 text-no-wrap font-weight-bold text-body"
                  :class="`${get(column, 'headerProps.class', '')} ${column.align === 'start' ? 'align-start' : ''}`"
                >
                  {{ column.title }}
                </div>
                <span v-if="!!column.ariaLabel" class="sr-only">{{ column.ariaLabel }}</span>
              </template>
            </th>
          </tr>
        </template>

        <template #item.uid="{ item }">
          {{ item.uid }}
        </template>

        <template #expanded-row="{ columns, item }">
          <tr>
            <td class="bg-surface-light px-4 pb-4" :colspan="columns.length">
              <pre class="bg-white pa-2">{{ JSON.stringify(item, null, 2) }}</pre>
            </td>
          </tr>
        </template>

        <template #item.edit="{ item }">
          <EditUserProfileModal
            :after-cancel="afterCancelUpdateUser"
            :after-update-user="afterEditUserProfile"
            :departments="departments"
            :disabled="isBecoming"
            :profile="item"
          />
        </template>

        <template #item.lastName="{ item }">
          <div class="name-container">
            <div class="icons">
              <span v-if="!item.canAccessCanvasData">
                <span class="c-letter">C</span>
                <span class="slash text-error">\</span>
              </span>
              <span v-if="!item.canAccessAdvisingData" class="advising-data">
                <span class="slash-2 text-error">\</span>
                <v-icon :icon="mdiNoteOutline" size="small" />
              </span>
            </div>
            <div v-if="!item.name" class="name">
              <span class="text-medium-emphasis">(Name unavailable)</span>
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
              <span class="font-weight-bold text-body text-success-darken-1">{{ department.name }} - {{ department.role }}</span>
              <div v-if="index !== item.departments.length - 1"></div>
            </div>
            <div v-if="item.canEditDegreeProgress || item.canReadDegreeProgress" class="text-medium-emphasis">
              <span class="font-weight-bold text-body">Degree Progress - </span>
              <span v-if="item.canEditDegreeProgress && item.canReadDegreeProgress" class="text-body"> read/write</span>
              <span v-if="!(item.canEditDegreeProgress && item.canReadDegreeProgress) && item.canReadDegreeProgress" class="text-body"> read</span>
              <span v-if="item.automateDegreeProgressPermission" class="text-body"> (automated)</span>
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
            <span v-if="item.lastLogin" class="text-body">{{ DateTime.fromISO(item.lastLogin).toFormat('DD') }}</span>
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
            v-if="canBecome(item) && !isBecoming"
            :id="`become-${item.uid}`"
            :aria-label="`Log in as ${item.name}`"
            class="text-primary"
            flat
            :icon="mdiLoginVariant"
            size="sm"
            @click="() => become(item.uid)"
          />
          <v-progress-circular
            v-if="isBecoming"
            color="primary"
            indeterminate
            size="16"
            width="2"
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
import {clone, debounce, find, get, isNil, lowerCase, map, size, trim} from 'lodash'
import {escapeForRegExp, normalizeId} from '@/lib/utils'
import {mdiEmail} from '@mdi/js'
import {mdiLoginVariant, mdiNoteOutline} from '@mdi/js'
import {ref, watch} from 'vue'
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
const isBecoming = ref(false)
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
  if (filterType.value === 'search') {
    putFocusNextTick('search-user-input')
  }
})

watch(() => props.refresh, value => {
  if (value) {
    fetchUsers()
  }
})

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
  isBecoming.value = true
  becomeUser(uid).then(() => {
    window.location.href = '/'
    isBecoming.value = false
  })
}

const canBecome = user => {
  const isNotMe = user.uid !== contextStore.currentUser.uid
  const expiredOrInactive = user.isExpiredPerLdap || user.deletedAt || user.isBlocked
  const hasAnyRole = user?.isAdmin || find(user.departments, (dept) => !isNil(dept.role))
  return contextStore.config.devAuthEnabled && isNotMe && !expiredOrInactive && hasAnyRole
}

const fetchUsers = (returnFocusId=null, srAlert='Loading users.') => {
  let isValidSelection = (filterType.value !== 'search') || get(userSelection.value, 'value.uid')

  let uidOfUser = undefined
  let searchFirstUser = false
  if (!isValidSelection && users.value.length === 1 && filterType.value === 'search') {
    isValidSelection = users.value[0].uid
    uidOfUser = users.value[0].uid
    searchFirstUser = true
  }

  if (isValidSelection) {
    const sortDescription = sortBy.value ? `; sorted by ${lowerCase(clone(sortBy.value))}, ${sortDesc.value ? 'descending' : 'ascending'}` : ''
    alertScreenReader(srAlert)
    isFetching.value = true
    totalUserCount.value = 0
    users.value = []
    switch(filterType.value) {
    case 'admins':
      getAdminUsers(sortBy.value, sortDesc.value, false).then(data => {
        users.value = data.users
        totalUserCount.value = data.totalUserCount
        isFetching.value = false
        alertScreenReader(`Admin users loaded${sortDescription}`)
        putFocusNextTick('user-filter-options')
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
        const department = find(props.departments, {'code': filterBy.value.deptCode})
        users.value = data.users
        totalUserCount.value = data.totalUserCount
        isFetching.value = false
        alertScreenReader(`${department.name} users loaded${sortDescription}`)
        putFocusNextTick(returnFocusId || 'department-select-list')
      })
      break
    case 'search':
      if (searchFirstUser === false) {
        uidOfUser = userSelection.value.value.uid
      }
      getUserByUid(uidOfUser, false).then(data => {
        users.value = [data]
        totalUserCount.value = 1
        isFetching.value = false
        userSelection.value = null
        alertScreenReader(`Search results loaded${sortDescription}`)
        putFocusNextTick('search-user-input')
      })
      break
    }
  }
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

const handleSort = sortKeys => {
  const sortKey = get(sortKeys, 0)
  if (sortKey) {
    sortBy.value = sortKey.key
    sortDesc.value = sortKey.order !== 'asc'
  } else {
    sortBy.value = null
    sortDesc.value = false
  }
  alertScreenReader('Sorting users.')
  fetchUsers(`admits-sort-by-${sortKey.key}-btn`, 'Sorting users.') // Fetch users with new sorting parameters
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

const quickLink = (role, deptCode=null, returnFocusId) => {
  filterType.value = 'filter'
  filterBy.value = {
    deptCode: deptCode,
    role: role,
    searchPhrase: '',
    status: 'active'
  }
  fetchUsers(returnFocusId)
}
</script>

<style>
.manifest-column-name {
  background-color: rgba(var(--v-theme-secondary), var(--v-medium-emphasis-opacity));
  color: rgb(var(--v-theme-primary));
  font-weight: 900;
}
.manifest-column-last-login {
  background-color: rgba(var(--v-theme-light-blue), var(--v-medium-emphasis-opacity));
  font-weight: 600;
}
</style>

<style scoped>
:deep(.v-table > .v-table__wrapper > table > thead > tr > th) {
  height: 40px !important;
}
.advising-data {
  position: relative;
  left: -8px;
}
.c-letter {
  position: relative;
  top: 1px;
  left: 1px;
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
.name-container {
  position: relative;
  top: -1px;
}
.not-sortable {
  opacity: 0.62;
  padding-top: 2px;
}
.quick-links-label {
  font-size: 18px;
  font-weight: 600;
  padding-bottom: 2px;
}
.row-padding {
  padding: 12px !important;
}
.select-menu {
  height: 40px;
}
.slash {
  font-size: 22px;
  left: -8px;
  position: relative;
  top: 4px;
}
.slash-2 {
  font-size: 22px;
  left: 12px;
  top: 4px;
  position: relative;
  z-index: 100;
}
</style>
