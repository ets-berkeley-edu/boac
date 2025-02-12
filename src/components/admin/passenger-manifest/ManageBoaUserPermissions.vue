<template>
  <div class="d-flex">
    <div class="w-33">
      <v-checkbox
        id="is-admin"
        v-model="user.isAdmin"
        color="primary"
        density="compact"
        :hide-details="true"
        label="Admin"
      />
      <v-checkbox
        id="is-blocked"
        v-model="user.isBlocked"
        color="primary"
        density="compact"
        :hide-details="true"
        label="Blocked"
      />
      <v-checkbox
        v-if="user.id"
        id="is-deleted"
        v-model="user.deletedAt"
        color="primary"
        density="compact"
        :hide-details="true"
        label="Deleted"
      />
    </div>
    <div>
      <v-checkbox
        id="can-access-canvas-data"
        v-model="user.canAccessCanvasData"
        color="primary"
        density="compact"
        :disabled="isPeerAdvisor(user)"
        :hide-details="true"
        label="Canvas Data"
      />
      <v-checkbox
        id="can-access-advising-data"
        v-model="user.canAccessAdvisingData"
        color="primary"
        density="compact"
        :disabled="isPeerAdvisor(user)"
        :hide-details="true"
        label="Notes and Appointments"
      />
    </div>
  </div>
  <v-expand-transition class="mt-1">
    <ManageDegreeProgressPermission v-show="isCoe(user) || user.degreeProgressPermission" v-model="user" />
  </v-expand-transition>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import ManageDegreeProgressPermission from '@/components/admin/passenger-manifest/ManageDegreeProgressPermission.vue'
import type {BoaUser} from '@/lib/types'
import {isCoe, isPeerAdvisor} from '@/lib/boa-user'

const user = defineModel<BoaUser>({
  required: true,
  type: Object as PropType<BoaUser>
})
</script>
