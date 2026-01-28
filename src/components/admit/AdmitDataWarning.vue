<template>
  <div
    v-if="updatedAt && DateTime.now().diff(updatedAt, 'hours').hours >= 24"
    class="align-center d-flex font-size-16 text-error"
  >
    <v-icon class="mr-1" :icon="mdiAlert" />
    <div aria-live="polite" class="font-weight-500">Admit data was last updated on <Date :date="updatedAt" :timezone="timezone" /></div>
  </div>
</template>

<script setup lang="ts">
import {DateTime} from 'luxon'
import {mdiAlert} from '@mdi/js'
import Date from '@/components/util/Date.vue'
import {useContextStore} from '@/stores/context'

defineProps({
  updatedAt: {
    default: undefined,
    required: false,
    type: String
  }
})
const timezone = useContextStore().config.timezone
</script>
