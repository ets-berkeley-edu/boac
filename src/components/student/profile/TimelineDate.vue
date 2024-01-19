<template>
  <div v-if="datePerTimezone && dateFormat">
    <span class="sr-only">{{ srPrefix }} </span>{{ $moment(datePerTimezone).format(dateFormat) }}
    <div v-if="includeTimeOfDay">
      {{ $moment(datePerTimezone).format('h:mma') }}
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'

export default {
  name: 'TimelineDate',
  mixins: [Context],
  props: {
    date: [Date, String],
    includeTimeOfDay: Boolean,
    srPrefix: String
  },
  data() {
    return {
      now: this.$moment()
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
      return this.$moment(this.date).tz(this.$config.timezone)
    }
  }
}
</script>
