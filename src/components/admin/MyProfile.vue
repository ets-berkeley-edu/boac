<template>
  <b-container class="m-3 pr-5" fluid>
    <b-row align-v="start" class="border-bottom border-top p-2">
      <b-col class="font-weight-500" cols="3">
        Name
      </b-col>
      <b-col>
        {{ $currentUser.name }}
      </b-col>
    </b-row>
    <b-row align-v="start" class="border-bottom p-2">
      <b-col class="font-weight-500" cols="3">
        UID
      </b-col>
      <b-col>
        {{ $currentUser.uid }}
      </b-col>
    </b-row>
    <b-row align-v="start" class="border-bottom p-2">
      <b-col class="font-weight-500" cols="3">
        Campus Solutions ID
      </b-col>
      <b-col>
        {{ $currentUser.csid }}
      </b-col>
    </b-row>
    <b-row align-v="start" class="border-bottom p-2">
      <b-col class="font-weight-500" cols="3">
        Email
      </b-col>
      <b-col>
        {{ $currentUser.email }}
      </b-col>
    </b-row>
    <b-row align-v="start" class="border-bottom p-2">
      <b-col class="font-weight-500 v-align-middle" cols="3">
        Roles
      </b-col>
      <b-col>
        <div v-if="$currentUser.isAdmin || !$currentUser.canAccessCanvasData">
          <span v-if="$currentUser.isAdmin">You are a BOA Admin user.</span>
          <span v-if="!$currentUser.canAccessCanvasData">You do not have access to bCourses (LMS) data.</span>
        </div>
        <div v-if="$currentUser.departments.length">
          <div v-for="department in $currentUser.departments" :key="department.code">
            <span>{{ oxfordJoin(getRoles(department)) }} in {{ department.name }}.</span>
          </div>
        </div>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import Util from '@/mixins/Util';

export default {
  name: 'MyProfile',
  mixins: [Util],
  data: () => ({
    dropInAdvisorDeptCodes: undefined
  }),
  created() {
    this.dropInAdvisorDeptCodes = this.map(this.$currentUser.dropInAdvisorStatus, 'deptCode');
  },
  methods: {
    conditionalAppend(items, item, append) {
      if (append) {
        items.push(item)
      }
    },
    getRoles(department) {
      const advisorType = this.includes(this.dropInAdvisorDeptCodes, department.code) ? 'Drop-in Advisor' : 'Advisor';
      const roles = [];
      this.conditionalAppend(roles, 'Director', department.isDirector);
      this.conditionalAppend(roles, advisorType, department.isAdvisor);
      this.conditionalAppend(roles, 'Scheduler', department.isScheduler);
      return roles;
    }
  }
}
</script>
