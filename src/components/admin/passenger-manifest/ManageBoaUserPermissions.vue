<template>
  <div>
    <div>
      <v-checkbox
        id="is-admin"
        v-model="user.isAdmin"
        color="primary"
        density="compact"
        :hide-details="true"
        :disabled="isPeerAdvisor(user) || !!user.departments.length"
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
        :disabled="isPeerAdvisor(user) || isPeerAdvisorManager(user)"
        :hide-details="true"
        label="Notes and Appointments"
      />
      <v-checkbox
        v-if="user.id && user.disabledAt"
        id="is-disabled"
        v-model="disabled"
        color="primary"
        density="compact"
        :hide-details="true"
        :label="`Disabled (${DateTime.fromISO(user.disabledAt).toFormat('MMM d, yyyy')})`"
      />
      <v-checkbox
        v-if="user.id"
        id="is-deleted"
        v-model="deleted"
        color="primary"
        density="compact"
        :hide-details="true"
        label="Deleted"
      />
    </div>
    <v-expand-transition class="mt-1">
      <ManageDegreeProgressPermission v-show="isCoe(user) || user.degreeProgressPermission" v-model="user" />
    </v-expand-transition>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {DateTime} from 'luxon'
import {ref, watch} from 'vue'
import ManageDegreeProgressPermission from '@/components/admin/passenger-manifest/ManageDegreeProgressPermission.vue'
import type {BoaUser} from '@/lib/types'
import {isCoe, isPeerAdvisor, isPeerAdvisorManager} from '@/lib/boa-user'

const user = defineModel<BoaUser>({
  required: true,
  type: Object as PropType<BoaUser>
})

const deleted = ref<boolean>(!!user.value.deletedAt)

const disabled = ref<boolean>(!!user.value.disabledAt)

watch(deleted, (value: boolean) => {
  user.value.deletedAt = value ? DateTime.local().toISO() : undefined
})

// The only effect of the "Disabled" checkbox is to remove disabled status when unchecked.
watch(disabled, (value: boolean) => {
  if (!value) {
    user.value.isDisabled = false
  } else {
    user.value.isDisabled = undefined
  }
})
</script>
