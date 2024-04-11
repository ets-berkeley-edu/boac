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
let adjustedDate
let dateFormat

if (props.date) {
  const date = typeof props.date === 'string' ? new Date(props.date) : props.date
  const timezone = useContextStore().config.timezone
  adjustedDate = DateTime.fromJSDate(date).setZone(timezone)
  dateFormat = adjustedDate.year === DateTime.now().year ? 'MMM d' : 'MMM d, yyyy'
}
</script>
