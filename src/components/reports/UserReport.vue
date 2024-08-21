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
        {key: 'name', headerProps: {class: 'pl-4'}, title: 'Name'},
        {key: 'depts', title: 'Department(s)'},
        {key: 'notesCreated', headerProps: {class: 'd-flex justify-end'}, title: 'Notes Created'},
        {key: 'lastLogin', headerProps: {class: 'text-right pr-1'}, title: 'Last Login'},
        {key: 'email', headerProps: {class: 'd-flex justify-center'}, title: 'Email'}
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
        const align = data.column.key === 'notesCreated' ? 'text-right' : (data.column.key === 'email' ? 'd-flex justify-center' : '')
        const bgColor = data.index % 2 === 0 ? 'bg-grey-lighten-4' : ''
        return {
          class: `${align} ${bgColor} font-size-16 py-2`,
          id: `td-user-${data.item.uid}-column-${data.column.key}`
        }
      }"
      :row-props="data => {
        const bgColor = data.index % 2 === 0 ? 'bg-grey-lighten-4' : ''
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
              :aria-label="`Go to UC Berkeley Directory page of ${item.name}`"
              :href="`https://www.berkeley.edu/directory/results?search-term=${item.name}`"
              class="ma-0"
              target="_blank"
            >
              {{ item.name }}
            </a>
          </div>
          <div v-if="!item.name" class="text-nowrap">
            <span class="faint-text">Name unavailable (UID: {{ item.uid }})</span>
          </div>
        </div>
      </template>
      <template #item.depts="{item}">
        <div v-for="dept in item.departments" :key="dept.code" class="pb-1">
          <span :id="`dept-${dept.code}-${item.uid}`">
            <span class="dept-name">{{ dept.name }}</span> ({{ oxfordJoin(getBoaUserRoles(item, dept)) }})
          </span>
        </div>
        <div v-if="item.isAdmin" class="dept-name">BOA Admin</div>
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
          ><v-icon color="primary" :icon="mdiEmail" /><span class="sr-only"> (will open new browser tab)</span></a>
        </span>
      </template>
      <template #expanded-row="{ columns, item }">
        <tr>
          <td :colspan="columns.length">
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
.v-data-table__td--expanded-row {
  color: #337ab7;
}

</style>
