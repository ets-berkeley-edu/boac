<template>
  <h2 v-if="admitDataWarning" class="has-error font-size-16 font-weight-bold">{{ admitDataWarning }}</h2>
</template>

<script>
export default {
  name: 'AdmitDataWarning',
  props: {
    updatedAt: {
      type: String,
      required: false
    }
  },
  computed: {
    admitDataWarning() {
      let warning = null
      if (this.updatedAt) {
        const localUpdatedAt = this.$moment(this.updatedAt).tz(this.$config.timezone)
        if (this.$moment.duration(this.now.diff(localUpdatedAt)).as('hours') >= 24) {
          warning = `Note: admit data was last updated on ${this.$options.filters.moment(localUpdatedAt, 'MMM D, YYYY')}`
        }
      }
      return warning
    }
  },
  created() {
    this.now = this.$moment()
  }
}
</script>