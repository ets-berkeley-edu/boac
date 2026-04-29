<template>
  <div v-if="adjustedDate" :class="{'font-size-14': includeTimeOfDay}">
    <span class="sr-only">{{ srPrefix }} </span>
    <div>
      <span :aria-hidden="true">
        {{ adjustedDate.toFormat(adjustedDate && adjustedDate.year === today.year ? 'MMM d' : 'MMM d, yyyy') }}
      </span>
      <span class="sr-only">
        {{ adjustedDate.toFormat(adjustedDate && adjustedDate.year === today.year ? 'MMMM d' : 'MMMM d, yyyy') }}
      </span>
      <span v-if="includeTimeOfDay">
        <span :aria-hidden="true"> @</span>
        <span class="sr-only">at</span>
        {{ adjustedDate.toFormat('h:mma') }}
      </span>
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
