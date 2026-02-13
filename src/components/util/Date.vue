<template>
  <component :is="tag">
    <span :aria-hidden="true">
      {{ dateTime.toLocaleString(format) }}
    </span>
    <span class="sr-only">
      {{ dateTime.toLocaleString(accessibleFormat) }}
    </span>
  </component>
</template>

<script setup>
import {computed} from 'vue'
import {DateTime} from 'luxon'
import {has} from 'lodash'

const props = defineProps({
  date: {
    required: true,
    type: String
  },
  format: {
    default: DateTime.DATE_MED,
    require: false,
    type: Object
  },
  sqlFormat: {
    required: false,
    type: Boolean
  },
  tag: {
    default: 'span',
    required: false,
    type: String
  },
  timezone: {
    default: null,
    required: false,
    type: String
  }
})

const accessibleFormat = computed(() => {
  const format = {
    ...props.format,
    month: 'long'
  }
  if (has(props.format, 'weekday')) {
    format['weekday'] = 'long'
  }
  return format
})

let dateTime
if (props.sqlFormat) {
  dateTime = DateTime.fromSQL(props.date)
} else {
  dateTime = DateTime.fromISO(props.date)
}
if (props.timezone) {
  dateTime = dateTime.setZone(props.timezone)
}
</script>
