My profile

<template>
  <v-container class="mr-5" fluid>
    <v-row
      v-for="(value, key) in profile"
      :key="key"
      align-v="start"
      class="border-bottom"
    >
      <v-col class="font-weight-bold" cols="5">
        {{ key }}
      </v-col>
      <v-col>
        <span v-html="value" />
      </v-col>
      <v-divider class="border-opacity-100"></v-divider>
    </v-row>
    <v-row align-v="start">
      <v-col class="font-weight-bold" cols="5">
        Roles
      </v-col>
      <v-col>
        <div v-if="currentUser.isAdmin" class="pv-3">You are a BOA Admin user.</div>
        <div v-if="!currentUser.canAccessCanvasData" class="pv-3">You do not have access to bCourses (LMS) data.</div>
        <div v-if="!currentUser.canAccessAdvisingData" class="pv-3">You do not have access to advising notes or appointments.</div>
        <div
          v-for="department in currentUser.departments"
          :key="department.code"
          class="flex-row pv-3"
        >
          <div id="my-dept-roles">{{ _upperFirst(department.role) }} in {{ department.name }}</div>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import {useContextStore} from '@/stores/context'
import Util from '@/mixins/Util'
import {isCoe} from '@/berkeley'

export default {
  name: 'MyProfile',
  mixins: [Util],
  data: () => ({
    profile: undefined,
    currentUser: undefined
  }),
  created() {
    this.profile = {
      Name: useContextStore().currentUser.name,
      UID: useContextStore().currentUser.uid,
      'Campus Solutions ID': useContextStore().currentUser.csid,
      Email: useContextStore().currentUser.email,
    }
    this.currentUser = {
      isAdmin: useContextStore().currentUser.isAdmin,
      canAccessCanvasData: useContextStore().currentUser.canAccessCanvasData,
      canAccessAdvisingData: useContextStore().currentUser.canAccessAdvisingData,
      departments: useContextStore().currentUser.departments
    }
    const memberships = []
    this._each(useContextStore().currentUser.departments, d => {
      if (d.role) {
        memberships.push({code: d.code, role: d.role})
      }
    })
    const permission = useContextStore().currentUser.degreeProgressPermission
    if (isCoe({departments: memberships}) || permission) {
      const permission = permission && this._capitalize(permission.replace('_', '/'))
      const automated = useContextStore().currentUser.automateDegreeProgressPermission
      this.profile['Degree Progress'] = permission ? `${permission} permission${automated ? ', per SIS profile data' : ' (managed by BOA service lead)'}` : '&mdash;'
    }
  }
}
</script>
