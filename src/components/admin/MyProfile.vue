<template>
  <v-container
    aria-labelledby="page-header"
    class="mr-5"
    fluid
    tag="dl"
  >
    <v-row
      v-for="(value, key) in profile"
      :key="key"
      align-v="start"
      no-gutters
    >
      <v-col class="font-weight-bold" cols="5" tag="dt">
        {{ key }}
      </v-col>
      <v-col tag="dd">
        <span v-html="value" />
      </v-col>
      <v-divider class="border-opacity-100" role="presentation" />
    </v-row>
    <v-row align-v="start" no-gutters>
      <v-col
        id="profile-roles-label"
        class="font-weight-bold"
        cols="5"
        tag="dt"
      >
        Roles
      </v-col>
      <v-col tag="dd">
        <ul aria-labelledby="profile-roles-label" class="list-no-bullets">
          <li v-if="currentUser.isAdmin" class="pv-3">You are a BOA Admin user.</li>
          <li v-if="!currentUser.canAccessCanvasData" class="pv-3">You do not have access to bCourses (LMS) data.</li>
          <li v-if="!currentUser.canAccessAdvisingData" class="pv-3">You do not have access to advising notes or appointments.</li>
          <li v-for="department in currentUser.departments" :key="department.deptCode">
            <BoaUserDepartmentsSummary id="my-dept-roles" :user="currentUser" />
          </li>
        </ul>
      </v-col>
      <v-divider class="border-opacity-100" role="presentation" />
    </v-row>
  </v-container>
</template>

<script setup>
import {capitalize, filter, map} from 'lodash'
import BoaUserDepartmentsSummary from '@/components/admin/passenger-manifest/BoaUserDepartmentsSummary.vue'
import {isCoe} from '@/lib/boa-user'
import {useContextStore} from '@/stores/context'

const currentUser = useContextStore().currentUser
const memberships = map(filter(currentUser.departments, 'role'), d => ({deptCode: d.deptCode, role: d.role}))
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
