<template>
  <div v-if="adjustedDate">
    <span class="sr-only">{{ srPrefix }} </span>
    {{ adjustedDate.toFormat(adjustedDate && adjustedDate.year === today.year ? 'MMM d' : 'MMM d, yyyy') }}
    <div v-if="includeTimeOfDay">
      {{ adjustedDate.toFormat('h:mma') }}
    </div>
  </div>
</template>

<script setup>
import {computed} from 'vue'
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

const today = DateTime.now()

const adjustedDate = computed(() => {
  let date
  if (props.date) {
    date = typeof props.date === 'string' ? DateTime.fromISO(props.date) : DateTime.fromJSDate(props.date)
  }
  return date ? date.setZone(useContextStore().config.timezone) : null
})
</script>
