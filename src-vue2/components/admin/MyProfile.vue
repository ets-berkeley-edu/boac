<template>
  <b-container class="mr-5" fluid>
    <b-row
      v-for="(value, key) in profile"
      :key="key"
      align-v="start"
      class="border-bottom p-2"
    >
      <b-col class="font-weight-500" cols="5">
        {{ key }}
      </b-col>
      <b-col>
        <span v-html="value" />
      </b-col>
    </b-row>
    <b-row align-v="start" class="p-2">
      <b-col class="font-weight-500 v-align-middle" cols="5">
        Roles
      </b-col>
      <b-col>
        <div v-if="currentUser.isAdmin" class="pb-3">You are a BOA Admin user.</div>
        <div v-if="!currentUser.canAccessCanvasData" class="pb-3">You do not have access to bCourses (LMS) data.</div>
        <div v-if="!currentUser.canAccessAdvisingData" class="pb-3">You do not have access to advising notes or appointments.</div>
        <div
          v-for="department in currentUser.departments"
          :key="department.code"
          class="flex-row pb-3"
        >
          <div id="my-dept-roles">{{ _upperFirst(department.role) }} in {{ department.name }}</div>
        </div>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import {isCoe} from '@/berkeley'

export default {
  name: 'MyProfile',
  mixins: [Context, Util],
  data: () => ({
    profile: undefined
  }),
  created() {
    this.profile = {
      Name: this.currentUser.name,
      UID: this.currentUser.uid,
      'Campus Solutions ID': this.currentUser.csid,
      Email: this.currentUser.email
    }
    const memberships = []
    this._each(this.currentUser.departments, d => {
      if (d.role) {
        memberships.push({code: d.code, role: d.role})
      }
    })
    const permission = this.currentUser.degreeProgressPermission
    if (isCoe({departments: memberships}) || permission) {
      const permission = permission && this._capitalize(permission.replace('_', '/'))
      const automated = this.currentUser.automateDegreeProgressPermission
      this.profile['Degree Progress'] = permission ? `${permission} permission${automated ? ', per SIS profile data' : ' (managed by BOA service lead)'}` : '&mdash;'
    }
  }
}
</script>
