<template>
  <div class="pr-3">
    <v-data-table-server
      v-model:expanded="expanded"
      class="responsive-data-table"
      density="compact"
      disable-pagination
      disable-sort
      :header-props="{class: 'font-size-14 font-weight-bold py-3 text-no-wrap'}"
      :headers="[
        {key: 'data-table-expand'},
        {key: 'name', headerProps: {class: 'text-medium-emphasis pl-4'}, title: 'Name'},
        {key: 'depts', headerProps: {class: 'text-medium-emphasis'}, title: 'Department(s)'},
        {key: 'notesCreated', align: 'end', headerProps: {class: 'text-medium-emphasis'}, title: 'Notes Created'},
        {key: 'lastLogin', align: 'end', headerProps: {class: 'text-medium-emphasis'}, title: 'Last Login'},
        {key: 'email', align: 'center', headerProps: {class: 'text-medium-emphasis'}, title: 'Email'}
      ]"
      hide-default-footer
      hide-no-data
      :items="users"
      :items-length="totalUserCount || 0"
      :items-per-page="0"
      :loading="totalUserCount === undefined"
      loading-text="Fetching users..."
      mobile-breakpoint="md"
      :cell-props="data => {
        const alignCenter = data.column.key === 'email'
        const alignEnd = ['lastLogin', 'notesCreated'].includes(data.column.key)
        const bgColor = data.index % 2 === 0 ? 'bg-surface-light' : ''
        return {
          align: alignEnd ? 'end' : (alignCenter ? 'center' : undefined),
          class: `${bgColor} font-size-16 py-2`,
          id: `td-user-${data.item.uid}-column-${data.column.key}`
        }
      }"
      :row-props="data => {
        const bgColor = data.index % 2 === 0 ? 'bg-surface-light' : ''
        return {
          class: `${bgColor}`,
          id: `tr-user-${data.item.uid}`
        }
      }"
      show-expand
    >
      <template #item.name="{item}">
        <div class="d-flex">
          <div v-if="item.name" class="text-nowrap">
            <span class="sr-only">Name</span>
            <a
              :id="`directory-link-${item.uid}`"
              :aria-label="`${item.name} UC Berkeley Directory page (opens in new window)`"
              :href="`https://www.berkeley.edu/directory/results?search-term=${item.name}`"
              class="ma-0"
              target="_blank"
            >
              {{ item.name }}
            </a>
          </div>
          <div v-if="!item.name" class="text-nowrap">
            <span class="text-medium-emphasis">Name unavailable (UID: {{ item.uid }})</span>
          </div>
        </div>
      </template>
      <template #item.depts="{item}">
        <div v-for="dept in item.departments" :key="dept.code" class="pb-1">
          <span :id="`dept-${dept.code}-${item.uid}`">
            <span class="dept-name text-success">{{ dept.name }}</span> ({{ oxfordJoin(getBoaUserRoles(item, dept)) }})
          </span>
        </div>
        <div v-if="item.isAdmin" class="dept-name text-success">BOA Admin</div>
      </template>
      <template #item.lastLogin="{item}">
        <div :id="`user-last-login-${item.uid}`">
          <span v-if="item.lastLogin">{{ DateTime.fromISO(item.lastLogin).toFormat('MMM dd, yyyy') }}</span>
          <span v-if="!item.lastLogin">&#8212;</span>
        </div>
      </template>
      <template #item.email="{item}">
        <span :id="`user-email-${item.uid}`">
          <a
            :aria-label="`Send email to ${item.name}`"
            :href="`mailto:${item.campusEmail}`"
            target="_blank"
          ><v-icon color="primary" :icon="mdiEmail" /><span class="sr-only"> (opens in new window)</span></a>
        </span>
      </template>
      <template #expanded-row="{ columns, item }">
        <tr>
          <td class="border-b-md border-e-md border-s-md pa-6" :colspan="columns.length">
            <pre :id="`user-details-${item.uid}`">{{ item }}</pre>
          </td>
        </tr>
      </template>
    </v-data-table-server>
  </div>
</template>

<script setup>
import {getUsersReport} from '@/api/reports'
import {getBoaUserRoles} from '@/berkeley'
import {mdiEmail} from '@mdi/js'
import {onMounted, ref, watch} from 'vue'
import {oxfordJoin} from '@/lib/utils'
import {DateTime} from 'luxon'

const props = defineProps({
  department: {
    required: true,
    type: Object
  }
})

const expanded = ref([])
const totalUserCount = ref(undefined)
const users = ref([])

watch(() => props.department, () => {
  refresh()
})

const refresh = () => {
  totalUserCount.value = undefined
  getUsersReport(props.department.code).then(data => {
    totalUserCount.value = data.totalUserCount
    users.value = data.users
  })
}

onMounted(refresh)
</script>

<style scoped>
.dept-name {
  font-weight: 500;
}
</style>
