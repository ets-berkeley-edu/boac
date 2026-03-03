<template>
  <div>
    <div
      v-if="totalUserCount > 0"
      class="sr-only"
    >
      Showing {{ pluralize('user', totalUserCount) }}
    </div>
    <v-data-table-virtual
      v-table-caption="'BOA Users'"
      :cell-props="data => {
        const padding = ['becomeUser', 'data-table-expand'].includes(data.column.key) ? 'px-0' : ''
        return {
          class: `${padding}`,
          'data-label': data.column.title,
          id: normalizeId(`td-user-${data.item.uid}-column-${data.column.key}`)
        }
      }"
      class="v-table-hidden-row-override"
      :class="{'stacked-table': $vuetify.display.width <= mobileBreakpoint}"
      disable-pagination
      :disable-sort="totalUserCount < 2"
      :expanded="expanded"
      :headers="[
        {key: 'data-table-expand', sortable: false, title: '', width: 40},
        {align: 'start', key: 'uid', title: 'UID'},
        {align: 'start', cellProps: {class: ['td-name']}, key: 'lastName', sortable: true, title: 'Name'},
        {align: 'start', title: 'Departments', key: 'departments', headerProps: {class: 'pl-3'}},
        {align: 'start', title: 'Status', key: 'deletedAt', sortable: false},
        {align: 'start', cellProps: {class: 'td-last-login'}, headerProps: {class: 'pl-8'}, key: 'createdAt', sortable: true, title: 'Created At'},
        {align: 'start', cellProps: {class: 'td-last-login'}, headerProps: {class: 'pl-8'}, key: 'lastLogin', sortable: true, title: 'Last Login'},
        {align: 'start', key: 'campusEmail', sortable: false, title: 'Email'},
        {cellProps: {class: 'pr-6'}, key: 'becomeUser', sortable: false, title: ''}
      ]"
      :hide-default-footer="true"
      :items-length="totalUserCount || 0"
      :items-per-page="0"
      :items="users"
      item-value="uid"
      :loading="isFetching"
      loading-text="Searching..."
      :row-props="data => {
        const bgColor = data.index % 2 === 0 ? 'bg-surface-light' : ''
        return {
          class: `${bgColor}`,
          id: `tr-user-${data.item.uid}`
        }
      }"
      :sort-by="[{key: manifestStore.sortBy, order: sortDescending ? 'desc' : 'asc'}]"
      show-expand
      @update:sort-by="handleSort"
    >
      <template #no-data>
        <div class="font-size-16 text-medium-emphasis py-15">
          No matching users found.
        </div>
      </template>
      <template #headers="{columns, isSorted, toggleSort, getSortIcon, sortBy: sortedBy}">
        <SortableTableHeader
          v-if="columns.length"
          :columns="columns"
          id-prefix="courses"
          :is-compact="$vuetify.display.width <= mobileBreakpoint"
          :is-sorted="isSorted"
          :set-order="handleSort"
          :sorted-by="sortedBy[0]"
          :sort-icon="getSortIcon"
          :toggle-sort="toggleSort"
        />
      </template>
      <template #item.uid="{ item }">
        <span class="font-weight-bold text-medium-emphasis">{{ item.uid }}</span>
      </template>

      <template #expanded-row="{ columns, index, item }">
        <tr>
          <td :class="{'bg-surface-light': index % 2 === 0}" class="border-b-md" :colspan="columns.length">
            <pre class="pb-8 pt-4">{{ JSON.stringify(item, null, 2) }}</pre>
          </td>
        </tr>
      </template>

      <template #item.lastName="{index, item}">
        <BoaUserFullName
          :index="index"
          :on-click-edit-user="onClickEditUser"
          :user="item"
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
            :on-cancel="() => onCancelEditUser(index)"
            :on-save="() => onUpdateUser(index, item.uid)"
          />
        </v-dialog>
      </template>

      <template #item.departments="{ item }">
        <div class="row-padding">
          <BoaUserDepartmentsSummary :user="item" />
        </div>
      </template>

      <template #item.deletedAt="{ item }">
        <div v-for="(status, index) in getUserStatuses(item)" :key="index">
          {{ status }}
        </div>
      </template>

      <template #item.createdAt="{ item }">
        <span :id="`user-created-at-${item.uid}`" class="font-weight-bold text-medium-emphasis">
          <span class="hidden-sm-and-up">Created </span>
          {{ DateTime.fromISO(item.createdAt).toFormat('DD') }}
        </span>
      </template>

      <template #item.lastLogin="{ item }">
        <span :id="`user-last-login-${item.uid}`" class="font-weight-bold text-medium-emphasis">
          <span v-if="item.lastLogin" class="hidden-sm-and-up">Last login </span>
          <span v-if="item.lastLogin">{{ DateTime.fromISO(item.lastLogin).toFormat('DD') }}</span>
          <span v-if="!item.lastLogin">&mdash;</span>
        </span>
      </template>

      <template #item.campusEmail="{ item }">
        <div class="text-center">
          <a
            :aria-label="`Send email to ${item.name} (opens in new tab)`"
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
          class="bg-transparent"
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
      <template #bottom />
    </v-data-table-virtual>
  </div>
</template>

<script setup>
import {cloneDeep, find, get} from 'lodash'
import {DateTime} from 'luxon'
import {mdiEmail, mdiLoginVariant} from '@mdi/js'
import {ref, watch} from 'vue'
import {storeToRefs} from 'pinia'
import BoaUserDepartmentsSummary from '@/components/admin/passenger-manifest/BoaUserDepartmentsSummary.vue'
import BoaUserFullName from '@/components/admin/passenger-manifest/BoaUserFullName.vue'
import EditUser from '@/components/admin/passenger-manifest/EditUser.vue'
import SortableTableHeader from '@/components/util/SortableTableHeader'
import {ADVISING_ROLE_TYPES, getDeptCodesPerRoles} from '@/lib/berkeley-department'
import {alertScreenReader, normalizeId, pluralize, putFocusNextTick} from '@/lib/utils'
import {becomeUser, getUserByUid} from '@/api/user'
import {useContextStore} from '@/stores/context'
import {useManifestStore} from '@/stores/manifest.js'

const props = defineProps({
  fetchUsers: {
    required: true,
    type: Function
  },
  refresh: {
    required: false,
    type: Boolean
  }
})

const contextStore = useContextStore()
const manifestStore = useManifestStore()
const {filter, isFetching, sortDescending, totalUserCount, users} = storeToRefs(manifestStore)
const dialogs = ref([])
const editUserModel = ref(undefined)
const expanded = ref([])
const isBecomingUid = ref(false)
const mobileBreakpoint = 1150

watch(() => props.refresh, value => {
  if (value) {
    props.fetchUsers()
  }
})

const afterEditUserProfile = user => {
  alertScreenReader(`${user.name} profile updated.`)
  if (filter.type === 'search') {
    manifestStore.setUidBeingEdited(user.uid)
  }
  props.fetchUsers()
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
  const expiredOrInactive = user.isExpiredPerLdap || user.deletedAt
  // Typically, one role (eg, advisor) is enough to authorize user. An exception to the rule is the
  // peer_advisor_manager (PAM) role whereby the user MUST have a second role: advisor or director.
  const validRoles = ADVISING_ROLE_TYPES.concat(['peer_advisor'])
  const hasAnyRole = user.isAdmin || getDeptCodesPerRoles(user, validRoles).length
  return contextStore.config.devAuthEnabled && isNotMe && !expiredOrInactive && hasAnyRole
}

const getUserStatuses = user => {
  const statuses = user.deletedAt ? ['Deleted'] : ['Active']
  if (user.disabledAt) {
    statuses.push('Disabled')
  }
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
    manifestStore.setSortBy(sortKey.key)
    manifestStore.setSortDescending(sortKey.order === 'desc')
  } else {
    manifestStore.setSortDescending(false)
  }
  alertScreenReader('Sorting users.')
}

const onCancelEditUser = index => {
  dialogs.value[index] = false
  putFocusNextTick(`edit-${editUserModel.value.uid}`)
  editUserModel.value = undefined
  alertScreenReader('Canceled')
}

const onClickEditUser = (index, uid) => {
  editUserModel.value = cloneDeep(find(users.value, ['uid', uid]))
  dialogs.value[index] = true
}

const onUpdateUser = (index, uid) => {
  dialogs.value[index] = false
  editUserModel.value = undefined
  getUserByUid(uid, true).then(data => {
    manifestStore.onUpdateUser(data)
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
.row-padding {
  padding: 12px !important;
}
</style>
