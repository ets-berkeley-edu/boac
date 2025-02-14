<template>
  <div>
    <SelectDepartmentMembershipRoles
      v-model="filter"
      class="pb-0 pl-0 pt-1 pr-6"
      :all-berkeley-departments="allBerkeleyDepartments"
      :disabled="isBecomingUid || isFetching"
      :fetch-users="fetchUsers"
    />
    <QuickLinks
      class="ml-2 mt-3"
      :disabled="isBecomingUid || isFetching"
      :on-click-peer-advising-quick-link="onClickPeerAdvisingQuickLink"
      :on-click-quick-link="onClickQuickLink"
    />
    <div
      v-if="totalUserCount > 0"
      class="sr-only"
    >
      Showing {{ pluralize('user', totalUserCount) }}
    </div>
    <SectionSpinner :loading="isFetching" />
    <v-data-table-server
      v-if="!isFetching && !isNaN(totalUserCount)"
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
        {key: 'data-table-expand', sortable: false, title: '', width: 40},
        {align: 'start', key: 'uid', sortable: false, title: 'UID'},
        {align: 'end', ariaLabel: 'edit user', cellProps: {class: ['td-name']}, key: 'edit', sortable: false, title: ''},
        {align: 'start', cellProps: {class: ['td-name']}, key: 'lastName', sortable: true, title: 'Name'},
        {align: 'start', title: 'Departments', key: 'departments', headerProps: {class: 'pl-3'}, sortable: false},
        {align: 'start', title: 'Status', key: 'deletedAt', sortable: false},
        {align: 'start', cellProps: {class: 'td-last-login'}, headerProps: {class: 'pl-8'}, key: 'lastLogin', sortable: true, title: 'Last Login'},
        {align: 'start', key: 'campusEmail', sortable: false, title: 'Email'},
        {key: 'becomeUser', sortable: false, title: ''}
      ]"
      :hide-default-footer="true"
      :items-length="totalUserCount || 0"
      :items-per-page="0"
      :items="users"
      :loading="isFetching"
      disable-pagination
      item-value="uid"
      loading-text="Searching..."
      no-data-text="No users"
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
            class="pt-3 text-no-wrap"
            :style="{width: column.width}"
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
                :disabled="!!isBecomingUid"
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
        <span class="font-weight-bold text-medium-emphasis">{{ item.uid }}</span>
      </template>

      <template #expanded-row="{ columns, item }">
        <tr>
          <td class="bg-surface-light px-4 pb-4" :colspan="columns.length">
            <pre class="bg-white pa-2">{{ JSON.stringify(item, null, 2) }}</pre>
          </td>
        </tr>
      </template>

      <template #item.edit="{index, item}">
        <v-btn
          :id="`edit-${item.uid}`"
          :aria-label="`Edit profile of ${item.name}`"
          color="primary"
          :icon="mdiNoteEditOutline"
          variant="text"
          width="20"
          @click="() => onClickEditUser(index, item.uid)"
        />
        <v-dialog
          v-model="dialogs[index]"
          aria-labelledby="modal-header"
          persistent
        >
          <EditUser
            v-if="editUserModel"
            v-model="editUserModel"
            :after-save="afterEditUserProfile"
            :all-berkeley-departments="allBerkeleyDepartments"
            :on-cancel="() => onCancelEditUser(index)"
            :on-save="() => onUpdateUser(index, item.uid)"
          />
        </v-dialog>
      </template>

      <template #item.lastName="{ item }">
        <BoaUserFullName :user="item" />
      </template>

      <template #item.departments="{ item }">
        <div class="row-padding">
          <div v-for="(department, index) in item.departments" :key="department.deptCode">
            <span class="font-weight-bold text-body text-success-darken-1">
              {{ department.deptName }} - {{ capitalize(map(department.memberships, 'role').join(', ')) }}
            </span>
            <div v-if="index !== item.departments.length - 1"></div>
          </div>
          <div v-if="item.canEditDegreeProgress || item.canReadDegreeProgress" class="text-medium-emphasis">
            <span class="font-weight-bold text-medium-emphasis">Degree Progress - </span>
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
        <span :id="`user-last-login-${item.uid}`" class="font-weight-bold text-medium-emphasis">
          <span v-if="item.lastLogin">{{ DateTime.fromISO(item.lastLogin).toFormat('DD') }}</span>
          <span v-if="!item.lastLogin">&mdash;</span>
        </span>
      </template>

      <template #item.campusEmail="{ item }">
        <div class="text-center">
          <a
            :aria-label="`Send email to ${item.name} (opens in new window)`"
            :href="`mailto:${item.campusEmail}`"
            target="_blank"
          >
            <v-icon :icon="mdiEmail" />
          </a>
        </div>
      </template>
      <template #item.becomeUser="{ item }">
        <v-btn
          v-if="canBecome(item) && item.uid !== isBecomingUid"
          :id="`become-${item.uid}`"
          :aria-label="`Log in as ${item.name}`"
          :class="{'text-primary': !isBecomingUid}"
          :disabled="!!isBecomingUid"
          flat
          :icon="mdiLoginVariant"
          size="sm"
          @click="() => become(item.uid)"
        />
        <v-progress-circular
          v-if="item.uid === isBecomingUid"
          color="primary"
          indeterminate
          size="16"
          width="2"
        />
      </template>
      <template #bottom></template>
    </v-data-table-server>
  </div>
</template>

<script setup>
import {DateTime} from 'luxon'
import {
  capitalize,
  clone,
  cloneDeep,
  find,
  get,
  indexOf,
  lowerCase,
  map
} from 'lodash'
import {mdiEmail, mdiLoginVariant, mdiNoteEditOutline} from '@mdi/js'
import {ref, watch} from 'vue'
import BoaUserFullName from '@/components/admin/passenger-manifest/BoaUserFullName.vue'
import EditUser from '@/components/admin/passenger-manifest/EditUser.vue'
import QuickLinks from '@/components/admin/passenger-manifest/QuickLinks.vue'
import SelectDepartmentMembershipRoles from '@/components/admin/passenger-manifest/SearchAndFilterBoaUsers.vue'
import SectionSpinner from '@/components/util/SectionSpinner.vue'
import {alertScreenReader, normalizeId, pluralize, putFocusNextTick} from '@/lib/utils'
import {becomeUser, getAdminUsers, getPeerAdvisingUsers, getUserByUid, getUsers} from '@/api/user'
import {getDeptCodesPerRoles} from '@/lib/berkeley-department'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  refresh: {
    required: false,
    type: Boolean
  },
  allBerkeleyDepartments: {
    required: true,
    type: Array
  }
})

const contextStore = useContextStore()

const dialogs = ref([])
const expanded = ref([])
const filter = ref({
  deptCode: 'QCADV',
  role: undefined,
  searchPhrase: '',
  status: undefined,
  type: 'search'
})
const isBecomingUid = ref(false)
const isFetching = ref(false)
const itemsPerPage = 10
const sortBy = ref('lastName')
const sortDesc = ref(false)
const totalUserCount = ref(NaN)
const editUserModel = ref(undefined)
const userSelection = ref()
const users = ref([])

watch(() => filter.value.type, () => {
  fetchUsers(filter.value.type === 'search' ? 'search-user-input' : undefined)
})

watch(() => props.refresh, value => {
  if (value) {
    fetchUsers()
  }
})

const afterEditUserProfile = user => {
  alertScreenReader(`${user.name} profile updated.`)
  if (filter.value.type === 'search') {
    userSelection.value = user.uid
  }
  fetchUsers()
  putFocusNextTick(get(user, 'uid') ? `edit-${user.uid}` : 'add-new-user-btn')
}

const become = uid => {
  isBecomingUid.value = uid
  becomeUser(uid).then(() => {
    window.location.href = '/'
  })
}

const canBecome = user => {
  const isNotMe = user.uid !== contextStore.currentUser.uid
  const expiredOrInactive = user.isExpiredPerLdap || user.deletedAt || user.isBlocked
  const hasAnyRole = user.isAdmin || getDeptCodesPerRoles(user, ['advisor', 'director']).length
  return contextStore.config.devAuthEnabled && isNotMe && !expiredOrInactive && hasAnyRole
}

const fetchUsers = (returnFocusId=null, srAlert='Loading users.') => {
  let isValidSelection = (filter.value.type !== 'search') || get(userSelection.value, 'value.uid')

  let uidOfUser = undefined
  let searchFirstUser = false
  if (!isValidSelection && users.value.length === 1 && filter.value.type === 'search') {
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
    const afterFetchUsers = (focusId, screenReaderAlert) => {
      userSelection.value = null
      isFetching.value = false
      alertScreenReader(screenReaderAlert)
      putFocusNextTick(focusId)
    }
    switch(filter.value.type) {
    case 'admins':
      getAdminUsers(sortBy.value, sortDesc.value, false).then(data => {
        users.value = data.users
        totalUserCount.value = data.totalUserCount
        afterFetchUsers('user-filter-options', `Admin users loaded${sortDescription}`)
      })
      break
    case 'filter':
      getUsers(
        filter.value.status === 'blocked',
        filter.value.status === 'deleted',
        filter.value.deptCode,
        'advisor',
        sortBy.value,
        sortDesc.value
      ).then(data => {
        users.value = data.users
        totalUserCount.value = data.totalUserCount
        afterFetchUsers(
          returnFocusId || 'department-select-list',
          `Department users loaded${sortDescription}`
        )
      })
      break
    case 'search':
      if (searchFirstUser === false) {
        uidOfUser = userSelection.value.value.uid
      }
      getUserByUid(uidOfUser, false).then(data => {
        users.value = [data]
        totalUserCount.value = 1
        afterFetchUsers('search-user-input', `Search results loaded${sortDescription}`)
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
  // Fetch users with new sorting parameters
  fetchUsers(`admits-sort-by-${sortKey.key}-btn`, 'Sorting users.')
}

const onCancelEditUser = index => {
  dialogs.value[index] = false
  putFocusNextTick(`edit-${editUserModel.value.uid}`)
  editUserModel.value = undefined
  alertScreenReader('Canceled')
}

const onClickEditUser = (index, uid) => {
  dialogs.value[index] = true
  editUserModel.value = cloneDeep(find(users.value, ['uid', uid]))
}

const onClickPeerAdvisingQuickLink = () => {
  isFetching.value = true
  getPeerAdvisingUsers().then(data => {
    users.value = data.users
    totalUserCount.value = data.totalUserCount
  }).then(() => {
    userSelection.value = undefined
    isFetching.value = false
    alertScreenReader('Peer Advising users have been loaded.')
    putFocusNextTick('quick-link-peer-advising')
  })
}

const onClickQuickLink = (deptCode, returnFocusId) => {
  filter.value = {
    deptCode: deptCode,
    role: undefined,
    searchPhrase: '',
    status: 'active',
    type: 'filter'
  }
  fetchUsers(returnFocusId)
}

const onUpdateUser = (index, uid) => {
  dialogs.value[index] = false
  editUserModel.value = undefined
  getUserByUid(uid, false).then(data => {
    const user = find(users.value, ['uid', uid])
    const index = indexOf(users.value, user)
    if (index !== -1) {
      users.value.splice(index, 1)
      users.value.splice(index, data)
    }
  })
}
</script>

<style>
.td-last-login {
  background-color: rgba(var(--v-theme-light-blue), var(--v-medium-emphasis-opacity));
  font-weight: 600;
}
.td-name {
  background-color: rgba(var(--v-theme-secondary), var(--v-medium-emphasis-opacity));
  color: rgb(var(--v-theme-primary));
  font-weight: 900;
}
</style>

<style scoped>
:deep(.v-table > .v-table__wrapper > table > thead > tr > th) {
  height: 40px !important;
}
.not-sortable {
  opacity: 0.62;
  padding-top: 2px;
}
.row-padding {
  padding: 12px !important;
}
</style>
