<template>
  <b-container class="mr-5" fluid>
    <b-row align-v="start" class="border-bottom p-2">
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
    <b-row align-v="start" class="p-2">
      <b-col class="font-weight-500 v-align-middle" cols="5">
        Roles
      </b-col>
      <b-col>
        <div v-if="$currentUser.isAdmin" class="pb-3">You are a BOA Admin user.</div>
        <div v-if="!$currentUser.canAccessCanvasData" class="pb-3">You do not have access to bCourses (LMS) data.</div>
        <div v-if="!$currentUser.canAccessAdvisingData" class="pb-3">You do not have access to advising notes or appointments.</div>
        <div
          v-for="department in $currentUser.departments"
          :key="department.code"
          class="flex-row pb-3">
          <div id="my-dept-roles">{{ upperFirst(department.role) }} in {{ department.name }}</div>
          <div v-if="$currentUser.canAccessAdvisingData && canToggleDropInAdvising(department)" class="ml-5">
            Drop-in advising:
            <DropInAdvisingToggle
              :dept-code="department.code"
              class="drop-in-advising-toggle" />
          </div>
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
  methods: {
    canToggleDropInAdvising: dept => dept.isDropInEnabled && (dept.role === 'advisor' || dept.role === 'director')
  }
}
</script>

<style scoped>
  .drop-in-advising-toggle {
    display: inline-block;
    padding-left: 5px;
  }
</style>
