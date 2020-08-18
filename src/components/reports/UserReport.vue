<template>
  <div class="pr-3">
    <b-table
      ref="users"
      :items="usersProvider"
      :fields="[
        {key: 'name', class: 'column-name font-weight-bolder pl-1'},
        {key: 'depts', label: 'Department(s)'},
        {key: 'notesCreated', class: 'text-nowrap text-right pr-3'},
        {key: 'lastLogin', class: 'column-last-login text-nowrap text-right pr-1'},
        {key: 'email', class: 'column-email text-center'}
      ]"
      hover
      responsive
      stacked="md"
      striped
      thead-class="text-nowrap">
      <template v-slot:cell(name)="row">
        <div class="d-flex">
          <div v-if="row.item.name" class="text-nowrap">
            <span class="sr-only">Name</span>
            <a
              :id="`directory-link-${row.item.uid}`"
              :aria-label="`Go to UC Berkeley Directory page of ${row.item.name}`"
              :href="`https://www.berkeley.edu/directory/results?search-term=${row.item.name}`"
              class="m-0"
              target="_blank">
              {{ row.item.name }}
            </a>
          </div>
          <div v-if="!row.item.name" class="text-nowrap">
            <span class="faint-text">Name unavailable (UID: {{ row.item.uid }})</span>
          </div>
        </div>
      </template>
      <template v-slot:cell(depts)="row">
        <div v-for="dept in row.item.departments" :key="dept.code" class="pb-1">
          <span :id="`dept-${dept.code}-${row.item.uid}`">
            <span class="dept-name">{{ dept.name }}</span> ({{ oxfordJoin(getBoaUserRoles(row.item, dept)) }})
          </span>
        </div>
        <div v-if="row.item.isAdmin" class="dept-name">BOA Admin</div>
      </template>
      <template v-slot:cell(lastLogin)="row">
        <div :id="`user-last-login-${row.item.uid}`">
          <span v-if="row.item.lastLogin">{{ row.item.lastLogin | moment('MMM D, YYYY') }}</span>
          <span v-if="!row.item.lastLogin">&#8212;</span>
        </div>
      </template>
      <template v-slot:cell(email)="row">
        <span :id="`user-email-${row.item.uid}`">
          <a
            :aria-label="`Send email to ${row.item.name}`"
            :href="`mailto:${row.item.campusEmail}`"
            target="_blank"><font-awesome icon="envelope" /><span class="sr-only"> (will open new browser tab)</span></a>
        </span>
      </template>
      <template v-slot:row-details="row">
        <b-card>
          <pre :id="`user-details-${row.item.uid}`">{{ row.item }}</pre>
        </b-card>
      </template>
    </b-table>
  </div>
</template>

<script>
import Berkeley from '@/mixins/Berkeley';
import Util from '@/mixins/Util';
import { getUsersReport } from "@/api/reports";

export default {
  name: 'UserReport',
  mixins: [Berkeley, Util],
  props: {
    department: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    isLoading: true,
    totalUserCount: undefined
  }),
  watch: {
    department() {
      this.$refs.users.refresh();
    }
  },
  methods: {
    usersProvider() {
      return getUsersReport(this.department.code).then(report => {
        this.totalUserCount = report.totalUserCount;
        return report.users;
      });
    }
  }
}
</script>

<style scoped>
.column-email {
  width: 50px;
}
.column-last-login {
  width: 120px;
}
.column-name {
  width: 200px;
}
.column-uid {
  width: 100px;
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
