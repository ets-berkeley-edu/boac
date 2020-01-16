<template>
  <b-container class="m-3 pr-5" fluid>
    <b-row align-v="start" class="border-bottom border-top p-2">
      <b-col class="font-weight-500" cols="5">
        Name
      </b-col>
      <b-col>
        {{ $currentUser.name }}
      </b-col>
    </b-row>
    <b-row align-v="start" class="border-bottom p-2">
      <b-col class="font-weight-500" cols="5">
        UID
      </b-col>
      <b-col>
        {{ $currentUser.uid }}
      </b-col>
    </b-row>
    <b-row align-v="start" class="border-bottom p-2">
      <b-col class="font-weight-500" cols="5">
        Campus Solutions ID
      </b-col>
      <b-col>
        {{ $currentUser.csid }}
      </b-col>
    </b-row>
    <b-row align-v="start" class="border-bottom p-2">
      <b-col class="font-weight-500" cols="5">
        Email
      </b-col>
      <b-col>
        {{ $currentUser.email }}
      </b-col>
    </b-row>
    <b-row align-v="start" class="border-bottom p-2">
      <b-col class="font-weight-500 v-align-middle" cols="5">
        Roles
      </b-col>
      <b-col>
        <div v-if="$currentUser.isAdmin" class="pb-3">You are a BOA Admin user.</div>
        <div v-if="!$currentUser.canAccessCanvasData" class="pb-3">You do not have access to bCourses (LMS) data.</div>
        <div
          v-for="department in $currentUser.departments"
          :key="department.code"
          class="flex-row pb-3">
          <DropInAdvisingToggle
            v-if="isDropInAdvisor(department.code)"
            :dept-code="department.code"
            class="drop-in-advising-toggle" />
          <div id="my-dept-roles">{{ oxfordJoin(getRoles(department)) }} in {{ department.name }}.</div>
        </div>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import Berkeley from '@/mixins/Berkeley';
import Context from '@/mixins/Context';
import DropInAdvisingToggle from '@/components/admin/DropInAdvisingToggle';
import Util from '@/mixins/Util';

export default {
  name: 'MyProfile',
  components: {
    DropInAdvisingToggle,
  },
  mixins: [Berkeley, Context, Util],
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
      const advisorType = this.isDropInAdvisor(department.code) ? 'Drop-in Advisor' : 'Advisor';
      const roles = [];
      this.conditionalAppend(roles, 'Director', department.isDirector);
      this.conditionalAppend(roles, advisorType, department.isAdvisor);
      this.conditionalAppend(roles, 'Scheduler', department.isScheduler);
      return roles;
    },
    isDropInAdvisor(deptCode) {
      return this.includes(this.dropInAdvisorDeptCodes, deptCode);
    }
  }
}
</script>

<style scoped>
  .drop-in-advising-toggle {
    margin-left: -87px;
    padding-right: 10px;
  }
</style>
