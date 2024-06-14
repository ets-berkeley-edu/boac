<template>
  <v-container class="mr-5" fluid>
    <v-row
      v-for="(value, key) in profile"
      :key="key"
      align-v="start"
      no-gutters
    >
      <v-col class="font-weight-bold" cols="5">
        {{ key }}
      </v-col>
      <v-col>
        <span v-html="value" />
      </v-col>
      <v-divider class="border-opacity-100"></v-divider>
    </v-row>
    <v-row align-v="start" no-gutters>
      <v-col class="font-weight-bold" cols="5">
        Roles
      </v-col>
      <v-col>
        <div v-if="currentUser.isAdmin" class="pv-3">You are a BOA Admin user.</div>
        <div v-if="!currentUser.canAccessCanvasData" class="pv-3">You do not have access to bCourses (LMS) data.</div>
        <div v-if="!currentUser.canAccessAdvisingData" class="pv-3">You do not have access to advising notes or appointments.</div>
        <div v-for="department in currentUser.departments" :key="department.code">
          <div id="my-dept-roles">{{ upperFirst(department.role) }} in {{ department.name }}</div>
        </div>
      </v-col>
      <v-divider class="border-opacity-100"></v-divider>
    </v-row>
  </v-container>
</template>

<script setup>
import {capitalize, filter, map, upperFirst} from 'lodash'
import {isCoe} from '@/berkeley'
import {useContextStore} from '@/stores/context'

const currentUser = useContextStore().currentUser
const memberships = map(filter(currentUser.departments, 'role'), d => ({code: d.code, role: d.role}))
const profile = {
  Name: currentUser.name,
  UID: currentUser.uid,
  'SIS ID': currentUser.csid,
  Email: currentUser.email,
}

if (isCoe({departments: memberships}) || currentUser.degreeProgressPermission) {
  const permission = currentUser.degreeProgressPermission && capitalize(currentUser.degreeProgressPermission.replace('_', '/'))
  const automated = currentUser.automateDegreeProgressPermission
  profile['Degree Progress'] = permission ? `${permission} permission${automated ? ', per SIS profile data' : ' (managed by BOA service lead)'}` : '&mdash;'
}
</script>
