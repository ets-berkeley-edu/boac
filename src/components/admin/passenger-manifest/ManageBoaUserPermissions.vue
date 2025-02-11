<template>
  <div class="d-flex">
    <div class="w-33">
      <v-checkbox
        id="is-admin"
        v-model="user.isAdmin"
        density="compact"
        label="Admin"
        color="primary"
        :hide-details="true"
      />
      <v-checkbox
        id="is-blocked"
        v-model="user.isBlocked"
        density="compact"
        color="primary"
        label="Blocked"
        :hide-details="true"
      />
      <v-checkbox
        v-if="user.id"
        id="is-deleted"
        v-model="user.deletedAt"
        density="compact"
        color="primary"
        label="Deleted"
        :value="Date()"
        :hide-details="true"
      />
    </div>
    <div>
      <v-checkbox
        id="can-access-canvas-data"
        v-model="user.canAccessCanvasData"
        density="compact"
        color="primary"
        label="Canvas Data"
        :hide-details="true"
      />
      <v-checkbox
        id="can-access-advising-data"
        v-model="user.canAccessAdvisingData"
        density="compact"
        color="primary"
        label="Notes and Appointments"
        :hide-details="true"
      />
    </div>
  </div>
  <div class="mt-3">
    <ManageDegreeProgressPermission
      v-if="isCoe(user) || user.degreeProgressPermission"
      v-model="user"
    />
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import ManageDegreeProgressPermission from '@/components/admin/passenger-manifest/ManageDegreeProgressPermission.vue'
import type {BoaUser} from '@/lib/types'
import {isCoe} from '@/lib/boa-user'

const user = defineModel<BoaUser>({
  required: true,
  type: Object as PropType<BoaUser>
})
</script>
