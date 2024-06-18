<template>
  <div v-if="adjustedDate">
    <span class="sr-only">{{ props.srPrefix }} </span>
    {{ adjustedDate.toFormat(dateFormat) }}
    <div v-if="props.includeTimeOfDay">
      {{ adjustedDate.toFormat('h:mma') }}
    </div>
  </div>
</template>

<script setup lang="ts">
import {DateTime} from 'luxon'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  date: {
    default: undefined,
    required: false,
    type: [Date, String]
  },
  includeTimeOfDay: {
    required: false,
    type: Boolean
  },
  srPrefix: {
    default: undefined,
    required: false,
    type: String
  }
})
const date = typeof props.date === 'string' ? new Date(props.date) : props.date
const adjustedDate = date ? DateTime.fromJSDate(date).setZone(useContextStore().config.timezone) : null
const dateFormat = adjustedDate && adjustedDate.year === DateTime.now().year ? 'MMM d' : 'MMM d, yyyy'
</script>
