<template>
  <div v-if="datePerTimezone && dateFormat">
    <span class="sr-only">{{ srPrefix }} </span>
    {{ DateTime.fromJSDate(datePerTimezone).toFormat(dateFormat) }}
    <div v-if="includeTimeOfDay">
      {{ DateTime.fromJSDate(datePerTimezone).toFormat('h:mma') }}
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import {DateTime} from 'luxon'

export default {
  name: 'TimelineDate',
  mixins: [Context, Util],
  props: {
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
  },
  data() {
    return {
      now: DateTime.now()
    }
  },
  computed: {
    dateFormat() {
      if (!this.datePerTimezone) {
        return null
      }
      return this.datePerTimezone.year() === this.now.year() ? 'MMM D' : 'MMM D, YYYY'
    },
    datePerTimezone() {
      if (!this.date) {
        return null
      }
      return DateTime.fromJSDate(this.date).setZone(this.config.timezone)
    }
  }
}
</script>
