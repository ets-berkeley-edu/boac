<template>
  <div
    v-if="localUpdatedAt && DateTime.now().diff(localUpdatedAt, 'hours').hours >= 24"
    class="align-center d-flex font-size-16 text-error"
  >
    <v-icon class="mr-1" :icon="mdiAlert" />
    <div aria-live="polite" class="font-weight-500" role="alert">Admit data was last updated on {{ localUpdatedAt.toLocaleString(DateTime.DATE_MED) }}</div>
  </div>
</template>

<script setup lang="ts">
import {DateTime} from 'luxon'
import {mdiAlert} from '@mdi/js'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  updatedAt: {
    default: undefined,
    required: false,
    type: String
  }
})
const timezone = useContextStore().config.timezone
const localUpdatedAt: DateTime<boolean> | undefined = props.updatedAt ? DateTime.fromISO(props.updatedAt).setZone(timezone) : undefined
</script>
