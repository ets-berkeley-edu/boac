<template>
  <div>
    <div
      v-if="totalUserCount > 0"
      class="sr-only"
    >
      Showing {{ pluralize('user', totalUserCount) }}
    </div>
    <v-data-table-virtual
      v-model:expanded="expanded"
      v-model:items-per-page="itemsPerPage"
      :cell-props="data => {
        const padding = ['becomeUser', 'data-table-expand'].includes(data.column.key) ? 'px-0' : ''
        return {
          class: `${padding}`,
          id: normalizeId(`td-user-${data.item.uid}-column-${data.column.key}`)
        }
      }"
      class="responsive-data-table v-table-hidden-row-override"
      :headers="[
        {key: 'data-table-expand', sortable: false, title: '', width: 40},
        {align: 'start', key: 'uid', title: 'UID'},
        {align: 'start', cellProps: {class: ['td-name']}, key: 'lastName', sortable: true, title: 'Name'},
        {align: 'start', title: 'Departments', key: 'departments', headerProps: {class: 'pl-3'}},
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
      :row-props="data => {
        const bgColor = data.index % 2 === 0 ? 'bg-surface-light' : ''
        return {
          class: `${bgColor}`,
          id: `tr-user-${data.item.uid}`
        }
      }"
      :disable-sort="totalUserCount < 2"
      :sort-by="[{key: manifestStore.sortBy, order: sortDescending ? 'desc' : 'asc'}]"
      show-expand
      @update:sort-by="handleSort"
    >
      <template #no-data>
        <div class="font-size-16 text-medium-emphasis py-15">
          No matching users found.
        </div>
      </template>
      <template #headers="{columns, isSorted, sortBy, toggleSort}">
        <tr>
          <th
            v-for="column in columns"
            :key="column.key"
            :aria-label="column.ariaLabel || column.title"
            :aria-sort="isSorted ? (sortDescending ? 'Descending' : 'Ascending') : null"
            class="pt-3 text-no-wrap"
            :style="{width: column.width}"
          >
            <template v-if="column.sortable">
              <v-btn
                v-if="totalUserCount > 1"
                :id="`admits-sort-by-${column.key}-btn`"
                :append-icon="sortBy[0].key === column.key ? (sortDescending ? mdiArrowDown : mdiArrowUp) : null"
                :aria-label="`Sort by ${column.ariaLabel || column.title} ${isSorted && sortDescending ? 'descending' : 'ascending'}`"
                class="font-size-14 font-weight-bold height-unset min-width-unset pa-1 text-body text-uppercase v-table-sort-btn-override"
                :class="{'align-start': column.align === 'start', 'icon-visible': isSorted}"
                density="compact"
                :disabled="!!isBecomingUid"
                variant="plain"
                @click="() => toggleSort(column)"
              >
                <span class="text-left">{{ column.title }}</span>
              </v-btn>
              <span
                v-if="totalUserCount < 2"
                class="font-size-14 font-weight-bold height-unset min-width-unset pa-1 text-left text-uppercase"
              >
                {{ column.title }}
              </span>
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
        <div class="mr-6">
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
        </div>
      </template>
      <template #bottom></template>
    </v-data-table-virtual>
  </div>
</template>

<script setup>
import {cloneDeep, find, get} from 'lodash'
import {DateTime} from 'luxon'
import {mdiArrowDown, mdiArrowUp, mdiEmail, mdiLoginVariant} from '@mdi/js'
import {ref, watch} from 'vue'
import {storeToRefs} from 'pinia'
import BoaUserDepartmentsSummary from '@/components/admin/passenger-manifest/BoaUserDepartmentsSummary.vue'
import BoaUserFullName from '@/components/admin/passenger-manifest/BoaUserFullName.vue'
import EditUser from '@/components/admin/passenger-manifest/EditUser.vue'
import {
  ADVISING_ROLE_TYPES,
  PEER_ADVISING_ROLE_TYPES,
  getDeptCodesPerRoles
} from '@/lib/berkeley-department'
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
const itemsPerPage = 10

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
  const validRoles = ADVISING_ROLE_TYPES.concat(PEER_ADVISING_ROLE_TYPES)
  const hasAnyRole = user.isAdmin || getDeptCodesPerRoles(user, validRoles).length
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
.not-sortable {
  opacity: 0.62;
  padding-top: 2px;
}
.row-padding {
  padding: 12px !important;
}
</style>
