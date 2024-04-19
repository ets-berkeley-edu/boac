<template>
  <div v-if="show" class="align-center d-flex font-size-16 text-error">
    <v-icon class="mr-1" :icon="mdiAlert" />
    <div aria-live="polite" class="font-weight-500" role="alert">Admit data was last updated on {{ localUpdatedAt }}</div>
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
let show = false
let localUpdatedAt = undefined

if (props.updatedAt) {
  const timezone = useContextStore().config.timezone
  localUpdatedAt = DateTime.fromISO(props.updatedAt).setZone(timezone).toLocaleString(DateTime.DATE_MED)
  show = DateTime.now().diff(localUpdatedAt, 'hours') >= 24
}
</script>
