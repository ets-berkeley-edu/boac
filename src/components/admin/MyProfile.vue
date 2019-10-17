<template>
  <b-container class="mb-3 mt-3">
    <b-row class="border-bottom border-top p-2">
      <b-col cols="3">
        Name
      </b-col>
      <b-col>
        {{ user.name }}
      </b-col>
    </b-row>
    <b-row class="border-bottom p-2">
      <b-col cols="3">
        UID
      </b-col>
      <b-col>
        {{ user.uid }}
      </b-col>
    </b-row>
    <b-row class="border-bottom p-2">
      <b-col cols="3">
        Campus Solutions ID
      </b-col>
      <b-col>
        {{ user.csid }}
      </b-col>
    </b-row>
    <b-row class="border-bottom p-2">
      <b-col cols="3">
        Email
      </b-col>
      <b-col>
        {{ user.email }}
      </b-col>
    </b-row>
    <b-row class="border-bottom p-2">
      <b-col cols="3">
        Roles and permissions
      </b-col>
      <b-col>
        <div v-if="user.departments.length">
          <div class="pt-1">
            <h3 class="color-grey font-size-14 font-weight-bold">{{ user.departments.length > 1 ? 'Departments' : 'Department' }}</h3>
          </div>
          <div>
            <div v-for="department in user.departments" :key="department.code">
              <span>{{ capitalize(oxfordJoin(getRoles(department)).toLowerCase()) }} in {{ department.name }}.</span>
            </div>
            <div v-if="user.isAdmin || !user.canAccessCanvasData">
              <span v-if="user.isAdmin">You are a BOA Admin user.</span>
              <span v-if="!user.canAccessCanvasData">You do not have access to bCourses (LMS) data.</span>
            </div>
          </div>
        </div>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'MyProfile',
  mixins: [UserMetadata, Util],
  methods: {
    conditionalAppend(items, item, append) {
      if (append) {
        items.push(item)
      }
    },
    getRoles(department) {
      const roles = [];
      this.conditionalAppend(roles, 'Director', department.isDirector);
      this.conditionalAppend(roles, 'Advisor', department.isAdvisor);
      this.conditionalAppend(roles, 'Drop-in Advisor', department.isDropInAdvisor);
      this.conditionalAppend(roles, 'Scheduler', department.isScheduler);
      return roles;
    }
  }
}
</script>
