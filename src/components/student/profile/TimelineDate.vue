<template>
  <div v-if="adjustedDate">
    <span class="sr-only">{{ srPrefix }} </span>
    {{ adjustedDate.toFormat(adjustedDate && adjustedDate.year === DateTime.now().year ? 'MMM d' : 'MMM d, yyyy') }}
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

const adjustedDate = computed(() => {
  const date = typeof props.date === 'string' ? new Date(props.date) : props.date
  return date ? DateTime.fromISO(props.date).setZone(useContextStore().config.timezone) : null
})
</script>
