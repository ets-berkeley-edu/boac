<template>
  <div v-if="datePerTimezone && dateFormat">
    <span class="sr-only">{{ srPrefix }} </span>{{ datePerTimezone | moment(dateFormat) }}
    <div v-if="includeTimeOfDay">
      {{ datePerTimezone | moment('h:mma') }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'TimelineDate',
  props: {
    date: String,
    includeTimeOfDay: Boolean,
    srPrefix: String
  },
  data: () => ({
    datePerTimezone: undefined,
    dateFormat: undefined,
    now: new Date(),
    timeOfDay: undefined
  }),
  watch: {
    date() {
      this.render();
    }
  },
  created() {
    this.render();
  },
  methods: {
    render() {
      if (this.date) {
        const now = this.$moment();
        this.datePerTimezone = this.$moment(this.date).utcOffset(now.utcOffset());
        this.dateFormat = this.datePerTimezone.year() === now.year() ? 'MMM D' : 'MMM D, YYYY';
      }
    }
  }
}
</script>
