<template>
  <div v-if="datePerTimezone && dateFormat">
    <span class="sr-only">{{ srPrefix }} </span>{{ moment(datePerTimezone).format(dateFormat) }}
    <div v-if="includeTimeOfDay">
      {{ moment(datePerTimezone).format('h:mma') }}
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'

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
      now: this.moment()
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
      return this.moment(this.date).tz(this.config.timezone)
    }
  }
}
</script>
